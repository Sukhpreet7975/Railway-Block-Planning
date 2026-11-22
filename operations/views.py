from datetime import date, datetime

from django.contrib import messages
from django.db import transaction
from django.db.models.deletion import ProtectedError
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from .decorators import admin_required, planner_or_admin_required
from .forms import (
    MaintenanceRequestForm,
    RailwaySectionForm,
    TrainForm,
    TrainScheduleForm,
)
from .models import (
    BlockPlan,
    MaintenanceRequest,
    RailwaySection,
    Train,
    TrainSchedule,
)
from .services.analytics import get_dashboard_analytics
from .services.block_planner import generate_block_recommendations
from .services.multi_request_optimizer import optimize_multiple_requests


# ============================================================
# Helper functions
# ============================================================

def get_candidate_times(candidate):
    """Support both recommendation key formats used by earlier versions."""
    start_time = candidate.get("start_time", candidate.get("start"))
    end_time = candidate.get("end_time", candidate.get("end"))
    return start_time, end_time


def candidate_has_conflict(maintenance_request, start_time, end_time):
    """Check a proposed slot against train schedules and active block plans."""
    if not start_time or not end_time or end_time <= start_time:
        return "The selected time slot is invalid."

    train_conflict = TrainSchedule.objects.filter(
        section=maintenance_request.section,
        start_time__lt=end_time,
        end_time__gt=start_time,
    ).exists()

    if train_conflict:
        return "The selected time slot conflicts with a train schedule."

    active_plan_conflict = BlockPlan.objects.filter(
        maintenance_request__section=maintenance_request.section,
        status__in=["PROPOSED", "APPROVED"],
        start_time__lt=end_time,
        end_time__gt=start_time,
    ).exists()

    if active_plan_conflict:
        return "The selected time slot conflicts with an existing block plan."

    already_has_active_plan = BlockPlan.objects.filter(
        maintenance_request=maintenance_request,
        status__in=["PROPOSED", "APPROVED"],
    ).exists()

    if already_has_active_plan:
        return "This maintenance request already has an active block plan."

    expected_minutes = maintenance_request.duration_minutes
    actual_minutes = int((end_time - start_time).total_seconds() // 60)

    if actual_minutes != expected_minutes:
        return "The selected slot duration does not match the maintenance request."

    return None


# ============================================================
# 1. HOME PAGE / DASHBOARD
# ============================================================

@planner_or_admin_required
def home(request):
    """Display the main dashboard with live database analytics."""

    planning_date = timezone.localdate()

    sections = RailwaySection.objects.all().order_by("id")

    maintenance_requests = (
        MaintenanceRequest.objects.select_related("section")
        .order_by("-created_at")[:5]
    )

    context = {
        "total_assets": RailwaySection.objects.filter(is_active=True).count(),
        "total_trains": Train.objects.count(),
        "pending_requests": MaintenanceRequest.objects.filter(
            status="PENDING"
        ).count(),
        "ai_status": "active",
        "sections": sections,
        "maintenance_requests": maintenance_requests,
        "planning_date": planning_date,
    }

    # Add calculated availability, block-plan counts and chart data.
    context.update(get_dashboard_analytics(planning_date))

    return render(request, "operations/dashboard.html", context)


# ============================================================
# 2. ABOUT PAGE
# ============================================================

def about(request):

    return render(
        request,
        'operations/about.html'
    )

# ============================================================
# 3. DASHBOARD PAGE
# ============================================================

@planner_or_admin_required
def dashboard(request):
    return home(request)


# ============================================================
# 4. RAILWAY SECTION CRUD OPERATIONS
# ============================================================

@planner_or_admin_required
def section_list(request):
    sections = RailwaySection.objects.all().order_by("id")
    return render(
        request,
        "operations/section_list.html",
        {"sections": sections},
    )


@admin_required
def section_create(request):
    if request.method == "POST":
        form = RailwaySectionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Railway section added successfully!")
            return redirect("section_list")
    else:
        form = RailwaySectionForm()

    return render(
        request,
        "operations/section_form.html",
        {"form": form, "title": "Add Railway Section"},
    )


@admin_required
def section_update(request, section_id):
    section = get_object_or_404(RailwaySection, id=section_id)

    if request.method == "POST":
        form = RailwaySectionForm(request.POST, instance=section)
        if form.is_valid():
            form.save()
            messages.success(request, "Railway section updated successfully!")
            return redirect("section_list")
    else:
        form = RailwaySectionForm(instance=section)

    return render(
        request,
        "operations/section_form.html",
        {"form": form, "title": "Update Railway Section"},
    )


@admin_required
def section_delete(request, section_id):
    section = get_object_or_404(RailwaySection, id=section_id)

    if request.method == "POST":
        try:
            section.delete()
            messages.success(request, "Railway section deleted successfully!")
        except ProtectedError:
            messages.error(
                request,
                "Cannot delete this section because it has related records.",
            )
        return redirect("section_list")

    return render(
        request,
        "operations/section_confirm_delete.html",
        {"section": section},
    )


@planner_or_admin_required
def assets(request):
    return redirect("section_list")


# ============================================================
# 5. TRAIN MANAGEMENT
# ============================================================

@planner_or_admin_required
def train_list(request):
    trains = Train.objects.all().order_by("id")
    return render(
        request,
        "operations/train_list.html",
        {"trains": trains},
    )


@admin_required
def train_create(request):
    if request.method == "POST":
        form = TrainForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Train added successfully!")
            return redirect("train_list")
    else:
        form = TrainForm()

    return render(
        request,
        "operations/train_form.html",
        {"form": form, "page_title": "Add Train"},
    )


@admin_required
def train_update(request, train_id):
    train = get_object_or_404(Train, id=train_id)

    if request.method == "POST":
        form = TrainForm(request.POST, instance=train)
        if form.is_valid():
            form.save()
            messages.success(request, "Train updated successfully!")
            return redirect("train_list")
    else:
        form = TrainForm(instance=train)

    return render(
        request,
        "operations/train_form.html",
        {"form": form, "page_title": "Edit Train"},
    )


@admin_required
def train_delete(request, train_id):
    train = get_object_or_404(Train, id=train_id)

    if request.method == "POST":
        try:
            train.delete()
            messages.success(request, "Train deleted successfully!")
        except ProtectedError:
            messages.error(
                request,
                "This train cannot be deleted because it has existing schedules.",
            )
        return redirect("train_list")

    return render(
        request,
        "operations/train_confirm_delete.html",
        {"train": train},
    )


# ============================================================
# 6. TRAIN SCHEDULE CRUD
# ============================================================

@planner_or_admin_required
def train_schedule_list(request):
    schedules = TrainSchedule.objects.select_related(
        "train", "section"
    ).order_by("start_time")

    return render(
        request,
        "operations/train_schedule_list.html",
        {"schedules": schedules},
    )


@admin_required
def train_schedule_create(request):
    if request.method == "POST":
        form = TrainScheduleForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Train schedule added successfully!")
            return redirect("train_schedule_list")
    else:
        form = TrainScheduleForm()

    return render(
        request,
        "operations/train_schedule_form.html",
        {"form": form, "page_title": "Add Train Schedule"},
    )


@admin_required
def train_schedule_update(request, schedule_id):
    schedule = get_object_or_404(TrainSchedule, id=schedule_id)

    if request.method == "POST":
        form = TrainScheduleForm(request.POST, instance=schedule)
        if form.is_valid():
            form.save()
            messages.success(request, "Train schedule updated successfully!")
            return redirect("train_schedule_list")
    else:
        form = TrainScheduleForm(instance=schedule)

    return render(
        request,
        "operations/train_schedule_form.html",
        {"form": form, "page_title": "Edit Train Schedule"},
    )


@admin_required
def train_schedule_delete(request, schedule_id):
    schedule = get_object_or_404(TrainSchedule, id=schedule_id)

    if request.method == "POST":
        schedule.delete()
        messages.success(request, "Train schedule deleted successfully!")
        return redirect("train_schedule_list")

    return render(
        request,
        "operations/train_schedule_confirm_delete.html",
        {"schedule": schedule},
    )


# ============================================================
# 7. MAINTENANCE REQUEST CRUD
# ============================================================

@planner_or_admin_required
def maintenance_request_list(request):
    maintenance_requests = MaintenanceRequest.objects.select_related(
        "section"
    ).order_by("-created_at")

    return render(
        request,
        "operations/maintenance_request_list.html",
        {"maintenance_requests": maintenance_requests},
    )


@planner_or_admin_required
def maintenance_request_create(request):
    if request.method == "POST":
        form = MaintenanceRequestForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Maintenance request submitted successfully!",
            )
            return redirect("maintenance_request_list")
    else:
        form = MaintenanceRequestForm()

    return render(
        request,
        "operations/maintenance_request_form.html",
        {"form": form, "page_title": "Submit Maintenance Request"},
    )


@admin_required
def maintenance_request_update(request, request_id):
    maintenance_request = get_object_or_404(
        MaintenanceRequest,
        id=request_id,
    )

    if request.method == "POST":
        form = MaintenanceRequestForm(
            request.POST,
            instance=maintenance_request,
        )
        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Maintenance request updated successfully!",
            )
            return redirect("maintenance_request_list")
    else:
        form = MaintenanceRequestForm(instance=maintenance_request)

    return render(
        request,
        "operations/maintenance_request_form.html",
        {"form": form, "page_title": "Edit Maintenance Request"},
    )


@admin_required
def maintenance_request_delete(request, request_id):
    maintenance_request = get_object_or_404(
        MaintenanceRequest,
        id=request_id,
    )

    if request.method == "POST":
        try:
            maintenance_request.delete()
            messages.success(
                request,
                "Maintenance request deleted successfully!",
            )
        except ProtectedError:
            messages.error(
                request,
                "Cannot delete this request because it has related block plans.",
            )
        return redirect("maintenance_request_list")

    return render(
        request,
        "operations/maintenance_request_confirm_delete.html",
        {"maintenance_request": maintenance_request},
    )


# ============================================================
# 8. RAILWAY SECTION DETAILS
# ============================================================

@planner_or_admin_required
def section_details(request, section_id):
    if section_id <= 0:
        raise Http404("Invalid Railway Section ID")

    section = get_object_or_404(RailwaySection, id=section_id)
    return HttpResponse(f"Railway Section: {section.name}")


# ============================================================
# 9. GET AND POST REQUEST DEMONSTRATION
# ============================================================

def request_demo(request):
    if request.method == "POST":
        return HttpResponse("POST Request Received!")

    return HttpResponse("This is a GET Request!")


# ============================================================
# 10. SINGLE-REQUEST AI RAILWAY BLOCK PLANNER
# ============================================================

@planner_or_admin_required
def ai_block_planner(request):
    pending_requests = MaintenanceRequest.objects.filter(
        status="PENDING"
    ).select_related("section").order_by("-created_at")

    planning_date = timezone.localdate()
    date_input = request.POST.get("planning_date") if request.method == "POST" else request.GET.get("planning_date")

    if date_input:
        try:
            planning_date = date.fromisoformat(date_input)
        except ValueError:
            messages.error(request, "Invalid planning date.")
            return redirect("ai_block_planner")

    request_id = (
        request.POST.get("request_id")
        if request.method == "POST"
        else request.GET.get("request_id")
    )

    if request_id:
        selected_request = get_object_or_404(
            pending_requests,
            id=request_id,
        )
    else:
        selected_request = pending_requests.first()

    planner_result = None

    if selected_request:
        planner_result = generate_block_recommendations(
            maintenance_request=selected_request,
            planning_date=planning_date,
        )

    if request.method == "POST":
        if not selected_request:
            messages.error(request, "There are no pending maintenance requests to plan.")
            return redirect("ai_block_planner")

        try:
            slot_index = int(request.POST.get("slot_index", ""))
            recommendations = planner_result["recommendations"]

            if slot_index < 0 or slot_index >= len(recommendations):
                messages.error(request, "Invalid recommendation selected.")
            else:
                selected_slot = recommendations[slot_index]
                start_time, end_time = get_candidate_times(selected_slot)

                with transaction.atomic():
                    locked_request = get_object_or_404(
                        MaintenanceRequest.objects.select_for_update(),
                        id=selected_request.id,
                        status="PENDING",
                    )

                    conflict_message = candidate_has_conflict(
                        locked_request,
                        start_time,
                        end_time,
                    )

                    if conflict_message:
                        messages.error(request, conflict_message)
                    else:
                        BlockPlan.objects.create(
                            maintenance_request=locked_request,
                            start_time=start_time,
                            end_time=end_time,
                            status="PROPOSED",
                        )

                        locked_request.status = "PLANNED"
                        locked_request.save(update_fields=["status"])

                        messages.success(
                            request,
                            "Block plan saved successfully as Proposed!",
                        )
                        return redirect("block_plan_list")

        except (ValueError, TypeError, KeyError):
            messages.error(request, "Invalid recommendation selection.")

    context = {
        "pending_requests": pending_requests,
        "selected_request": selected_request,
        "planning_date": planning_date,
        "planner_result": planner_result,
    }

    return render(
        request,
        "operations/ai_block_planner.html",
        context,
    )


# ============================================================
# 11. SAVED BLOCK PLANS AND ADMIN WORKFLOW
# ============================================================

@planner_or_admin_required
def block_plan_list(request):
    block_plans = BlockPlan.objects.select_related(
        "maintenance_request",
        "maintenance_request__section",
    ).order_by("-created_at")

    return render(
        request,
        "operations/block_plan_list.html",
        {"block_plans": block_plans},
    )


@admin_required
@require_POST
def approve_block_plan(request, plan_id):
    plan = get_object_or_404(BlockPlan, id=plan_id)

    if plan.status != "PROPOSED":
        messages.error(request, "Only proposed plans can be approved.")
        return redirect("block_plan_list")

    plan.status = "APPROVED"
    plan.save(update_fields=["status"])

    messages.success(request, "Block plan approved successfully.")
    return redirect("block_plan_list")


@admin_required
@require_POST
def cancel_block_plan(request, plan_id):
    with transaction.atomic():
        plan = get_object_or_404(
            BlockPlan.objects.select_for_update(),
            id=plan_id,
        )

        if plan.status not in ["PROPOSED", "APPROVED"]:
            messages.error(request, "This block plan cannot be cancelled.")
            return redirect("block_plan_list")

        plan.status = "CANCELLED"
        plan.save(update_fields=["status"])

        maintenance_request = plan.maintenance_request

        # Reopen the request only when it has no other active plan.
        another_active_plan_exists = BlockPlan.objects.filter(
            maintenance_request=maintenance_request,
            status__in=["PROPOSED", "APPROVED"],
        ).exists()

        if not another_active_plan_exists:
            maintenance_request.status = "PENDING"
            maintenance_request.save(update_fields=["status"])

    messages.success(request, "Block plan cancelled successfully.")
    return redirect("block_plan_list")


# ============================================================
# 12. MULTIPLE-REQUEST OPTIMIZER
# ============================================================

@planner_or_admin_required
def optimize_all_requests(request):
    planning_date_value = request.GET.get(
        "planning_date",
        timezone.localdate().isoformat(),
    )

    try:
        planning_date = date.fromisoformat(planning_date_value)
    except ValueError:
        planning_date = timezone.localdate()
        messages.error(request, "Invalid planning date.")

    result = optimize_multiple_requests(planning_date)

    context = {
        "planning_date": planning_date,
        "scheduled": result["scheduled"],
        "unscheduled": result["unscheduled"],
        "solver_status": result["solver_status"],
    }

    return render(
        request,
        "operations/multi_request_optimizer.html",
        context,
    )


# ============================================================
# 13. SAVE MULTIPLE OPTIMIZED PLANS
# ============================================================

@planner_or_admin_required
@require_POST
def save_optimized_plans(request):
    planning_date_value = request.POST.get("planning_date", "")

    try:
        planning_date = date.fromisoformat(planning_date_value)
    except ValueError:
        messages.error(request, "Please select a valid planning date.")
        return redirect("optimize_all_requests")

    validated_slots = []
    errors = []

    with transaction.atomic():
        locked_requests = list(
            MaintenanceRequest.objects.select_for_update().filter(
                status="PENDING"
            )
        )
        pending_ids = {maintenance_request.id for maintenance_request in locked_requests}

        # Re-run the optimizer on the server; do not trust browser-submitted slots.
        result = optimize_multiple_requests(planning_date)
        scheduled = result["scheduled"]

        if not scheduled:
            messages.warning(
                request,
                "There are no requests to save for this planning date.",
            )
            return redirect(
                f"{reverse('optimize_all_requests')}?planning_date={planning_date}"
            )

        for item in scheduled:
            maintenance_request = item["request"]
            candidate = item["candidate"]
            start_time, end_time = get_candidate_times(candidate)

            if maintenance_request.id not in pending_ids:
                errors.append(
                    f"Request #{maintenance_request.id} is no longer pending."
                )
                continue

            conflict_message = candidate_has_conflict(
                maintenance_request,
                start_time,
                end_time,
            )

            if conflict_message:
                errors.append(
                    f"Request #{maintenance_request.id}: {conflict_message}"
                )
                continue

            # Check overlaps with other recommendations in this batch.
            batch_conflict = False

            for saved_item in validated_slots:
                saved_request = saved_item["request"]
                saved_start, saved_end = get_candidate_times(
                    saved_item["candidate"]
                )

                if saved_request.section_id != maintenance_request.section_id:
                    continue

                if start_time < saved_end and saved_start < end_time:
                    batch_conflict = True
                    break

            if batch_conflict:
                errors.append(
                    f"Request #{maintenance_request.id} overlaps another selected request."
                )
                continue

            validated_slots.append(item)

        # Save all selected plans or none of them.
        if errors:
            messages.error(
                request,
                "No plans were saved. " + " ".join(errors),
            )
            return redirect(
                f"{reverse('optimize_all_requests')}?planning_date={planning_date}"
            )

        for item in validated_slots:
            maintenance_request = item["request"]
            candidate = item["candidate"]
            start_time, end_time = get_candidate_times(candidate)

            BlockPlan.objects.create(
                maintenance_request=maintenance_request,
                start_time=start_time,
                end_time=end_time,
                status="PROPOSED",
            )

            maintenance_request.status = "PLANNED"
            maintenance_request.save(update_fields=["status"])

    messages.success(
        request,
        f"{len(validated_slots)} optimized block plans saved successfully as Proposed.",
    )
    return redirect("block_plan_list")

# ==========================================
# REPORTS PAGE
# ==========================================

@planner_or_admin_required
def reports(request):

    planning_date = timezone.localdate()

    context = get_dashboard_analytics(planning_date)

    context.update({

        'planning_date': planning_date,

        'block_plans': BlockPlan.objects.select_related(
            'maintenance_request',
            'maintenance_request__section'
        ).order_by('-created_at'),

        'maintenance_requests': MaintenanceRequest.objects.select_related(
            'section'
        ).order_by('-created_at'),

    })

    return render(
        request,
        'operations/reports.html',
        context
    )
