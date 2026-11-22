from datetime import datetime, time

from django.utils import timezone

from operations.models import (
    RailwaySection,
    Train,
    MaintenanceRequest,
    BlockPlan,
)


def merge_intervals(intervals):
    """
    Merge overlapping time intervals to avoid counting
    the same blocked time more than once.
    """

    if not intervals:
        return []

    intervals.sort(key=lambda item: item[0])

    merged = [intervals[0]]

    for current_start, current_end in intervals[1:]:

        previous_start, previous_end = merged[-1]

        if current_start <= previous_end:

            merged[-1] = (
                previous_start,
                max(previous_end, current_end)
            )

        else:
            merged.append((current_start, current_end))

    return merged


def get_dashboard_analytics(planning_date):
    """
    Calculate dashboard statistics for the selected planning date.

    Planning window: 07:00 AM to 10:00 PM.

    Proposed and approved block plans count as blocked time.
    Cancelled and completed plans are excluded.
    """

    # Create the daily planning window.
    window_start = timezone.make_aware(
        datetime.combine(planning_date, time(7, 0))
    )

    window_end = timezone.make_aware(
        datetime.combine(planning_date, time(22, 0))
    )

    total_window_minutes = int(
        (window_end - window_start).total_seconds() / 60
    )

    # Get all active railway sections.
    sections = RailwaySection.objects.filter(
        is_active=True
    )

    total_sections = sections.count()

    # Initialize availability calculations.
    total_available_minutes = 0
    total_blocked_minutes = 0

    section_labels = []
    section_block_hours = []

    # Calculate availability for each active section.
    for section in sections:

        # Find proposed and approved plans that overlap
        # the selected day's planning window.
        plans = BlockPlan.objects.filter(
            maintenance_request__section=section,
            status__in=['PROPOSED', 'APPROVED'],
            start_time__lt=window_end,
            end_time__gt=window_start
        )

        intervals = []

        for plan in plans:

            # Clip each plan to the planning window.
            clipped_start = max(
                plan.start_time,
                window_start
            )

            clipped_end = min(
                plan.end_time,
                window_end
            )

            if clipped_start < clipped_end:

                intervals.append(
                    (clipped_start, clipped_end)
                )

        # Merge overlapping intervals.
        merged_intervals = merge_intervals(intervals)

        # Calculate total blocked minutes.
        blocked_minutes = sum(
            int(
                (end - start).total_seconds() / 60
            )
            for start, end in merged_intervals
        )

        # Calculate available minutes for this section.
        available_minutes = max(
            0,
            total_window_minutes - blocked_minutes
        )

        # Update overall totals.
        total_blocked_minutes += blocked_minutes
        total_available_minutes += available_minutes

        # Store chart data.
        section_labels.append(section.section_code)

        section_block_hours.append(
            round(blocked_minutes / 60, 2)
        )

    # Calculate total possible section-hours.
    total_section_minutes = (
        total_sections * total_window_minutes
    )

    # Calculate planned availability percentage.
    if total_section_minutes > 0:

        availability_percent = round(
            (
                total_available_minutes
                / total_section_minutes
            ) * 100,
            2
        )

    else:
        availability_percent = 0

    # Count proposed plans overlapping the planning window.
    proposed_plans = BlockPlan.objects.filter(
        status='PROPOSED',
        start_time__lt=window_end,
        end_time__gt=window_start
    ).count()

    # Count approved plans overlapping the planning window.
    approved_plans = BlockPlan.objects.filter(
        status='APPROVED',
        start_time__lt=window_end,
        end_time__gt=window_start
    ).count()

    # Prepare dashboard context.
    context = {

        # General statistics.
        'total_sections': total_sections,

        'total_trains': Train.objects.count(),

        'pending_requests': MaintenanceRequest.objects.filter(
            status='PENDING'
        ).count(),

        # Block plan statistics for selected planning date.
        'proposed_plans': proposed_plans,

        'approved_plans': approved_plans,

        # Completed requests across all dates.
        'completed_requests': MaintenanceRequest.objects.filter(
            status='COMPLETED'
        ).count(),

        # Availability statistics.
        'availability_percent': availability_percent,

        'total_available_hours': round(
            total_available_minutes / 60,
            2
        ),

        'total_blocked_hours': round(
            total_blocked_minutes / 60,
            2
        ),

        # Chart data.
        'section_labels': section_labels,

        'section_block_hours': section_block_hours,

    }

    return context