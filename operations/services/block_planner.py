
from datetime import datetime, time, timedelta

from django.utils import timezone

from operations.models import TrainSchedule, BlockPlan


def make_aware_datetime(date_value, time_value):
    """
    Combine a date and time into a timezone-aware datetime.
    """

    naive_datetime = datetime.combine(date_value, time_value)

    return timezone.make_aware(
        naive_datetime,
        timezone.get_current_timezone()
    )


def merge_intervals(intervals):
    """
    Merge overlapping occupied time intervals.
    """

    if not intervals:
        return []

    intervals.sort(key=lambda interval: interval[0])

    merged = [intervals[0]]

    for current_start, current_end in intervals[1:]:

        previous_start, previous_end = merged[-1]

        if current_start <= previous_end:

            merged[-1] = (
                previous_start,
                max(previous_end, current_end)
            )

        else:

            merged.append((
                current_start,
                current_end
            ))

    return merged


def find_free_windows(window_start, window_end, occupied_intervals):
    """
    Find free time windows between occupied intervals.
    """

    free_windows = []

    current_time = window_start

    for occupied_start, occupied_end in occupied_intervals:

        if occupied_start > current_time:

            free_windows.append((
                current_time,
                occupied_start
            ))

        current_time = max(
            current_time,
            occupied_end
        )

    if current_time < window_end:

        free_windows.append((
            current_time,
            window_end
        ))

    return free_windows


def generate_block_recommendations(
    maintenance_request,
    planning_date,
    work_start=time(7, 0),
    work_end=time(22, 0)
):
    """
    Generate available maintenance slots for one request,
    one railway section and one planning date.
    """

    # 1. Calculate planning window

    window_start = make_aware_datetime(
        planning_date,
        work_start
    )

    window_end = make_aware_datetime(
        planning_date,
        work_end
    )

    if window_end <= window_start:

        raise ValueError(
            "Planning end time must be after start time."
        )

    # 2. Calculate required maintenance duration

    required_duration = timedelta(
        minutes=maintenance_request.duration_minutes
    )

    # 3. Find overlapping train schedules

    schedules = TrainSchedule.objects.filter(
        section=maintenance_request.section,
        start_time__lt=window_end,
        end_time__gt=window_start
    ).order_by('start_time')

    # 4. Collect occupied intervals

    occupied_intervals = []

    # Train schedule intervals

    for schedule in schedules:

        occupied_start = max(
            schedule.start_time,
            window_start
        )

        occupied_end = min(
            schedule.end_time,
            window_end
        )

        occupied_intervals.append((
            occupied_start,
            occupied_end
        ))

    # 5. Include existing active block plans

    existing_plans = BlockPlan.objects.filter(
        maintenance_request__section=maintenance_request.section,
        status__in=['PROPOSED', 'APPROVED'],
        start_time__lt=window_end,
        end_time__gt=window_start
    ).exclude(
        maintenance_request=maintenance_request
    )

    for plan in existing_plans:

        occupied_start = max(
            plan.start_time,
            window_start
        )

        occupied_end = min(
            plan.end_time,
            window_end
        )

        occupied_intervals.append((
            occupied_start,
            occupied_end
        ))

    # 6. Merge overlapping occupied intervals

    merged_intervals = merge_intervals(
        occupied_intervals
    )

    # 7. Find available windows

    free_windows = find_free_windows(
        window_start,
        window_end,
        merged_intervals
    )

    # 8. Get preferred maintenance time

    preferred_start = None

    if maintenance_request.preferred_start:

        preferred_time = timezone.localtime(
            maintenance_request.preferred_start
        ).time()

        preferred_start = make_aware_datetime(
            planning_date,
            preferred_time
        )

    recommendations = []

    # 9. Check available windows

    for free_start, free_end in free_windows:

        available_duration = free_end - free_start

        # Check whether maintenance can fit

        if available_duration < required_duration:

            continue

        latest_possible_start = (
            free_end - required_duration
        )

        # Select the proposed start time

        if preferred_start:

            proposed_start = max(
                free_start,
                min(
                    preferred_start,
                    latest_possible_start
                )
            )

        else:

            proposed_start = free_start

        proposed_end = (
            proposed_start + required_duration
        )

        # Calculate difference from preferred time

        if preferred_start:

            difference_minutes = int(
                abs(
                    (
                        proposed_start - preferred_start
                    ).total_seconds()
                ) / 60
            )

        else:

            difference_minutes = 0

        # Store recommendation

        recommendations.append({

            'gap_start': free_start,

            'gap_end': free_end,

            'start': proposed_start,

            'end': proposed_end,

            'difference_minutes': difference_minutes,

            'available_minutes': int(
                available_duration.total_seconds() / 60
            )

        })

    # 10. Sort recommendations

    recommendations.sort(
        key=lambda item: (
            item['difference_minutes'],
            item['start']
        )
    )

    # 11. Return planning results

    return {

        'recommendations': recommendations,

        'total_schedules_checked': schedules.count(),

        'occupied_intervals': merged_intervals,

        'free_windows': free_windows,

        'planning_start': window_start,

        'planning_end': window_end

    }
