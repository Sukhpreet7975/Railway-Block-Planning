
from ortools.sat.python import cp_model

from operations.models import MaintenanceRequest
from operations.services.block_planner import (
    generate_block_recommendations
)


PRIORITY_WEIGHTS = {
    'CRITICAL': 100000,
    'HIGH': 80000,
    'MEDIUM': 60000,
    'LOW': 40000,
}


def normalize_candidate(candidate):
    """
    Standardize candidate dictionary keys.

    Supports:
        start / end
        start_time / end_time

    Returns:
        A dictionary containing start_time and end_time.
    """

    candidate = dict(candidate)

    start_time = (
        candidate.get('start_time')
        or candidate.get('start')
    )

    end_time = (
        candidate.get('end_time')
        or candidate.get('end')
    )

    if start_time is None or end_time is None:
        raise ValueError(
            "Invalid recommendation: start or end time is missing."
        )

    candidate['start_time'] = start_time
    candidate['end_time'] = end_time

    return candidate


def optimize_multiple_requests(planning_date):

    model = cp_model.CpModel()

    # Get all pending maintenance requests.
    requests = MaintenanceRequest.objects.filter(
        status='PENDING'
    ).select_related(
        'section'
    ).order_by('-created_at')

    request_candidates = {}
    all_candidates = []
    variables = {}

    # STEP 1: Generate recommendations for every request.
    for maintenance_request in requests:

        result = generate_block_recommendations(
            maintenance_request,
            planning_date
        )

        raw_candidates = result.get('recommendations', [])

        # Normalize all recommendation dictionaries.
        candidates = [
            normalize_candidate(candidate)
            for candidate in raw_candidates
        ]

        request_candidates[maintenance_request.id] = {
            'request': maintenance_request,
            'candidates': candidates
        }

        for index, candidate in enumerate(candidates):

            all_candidates.append({
                'request': maintenance_request,
                'candidate': candidate,
                'index': index
            })

    # STEP 2: Create decision variables.
    for item in all_candidates:

        request_id = item['request'].id
        index = item['index']

        variables[(request_id, index)] = model.NewBoolVar(
            f'request_{request_id}_slot_{index}'
        )

    # STEP 3: Each request can have at most one selected slot.
    for request_id, data in request_candidates.items():

        candidates = data['candidates']

        if not candidates:
            continue

        slot_variables = [
            variables[(request_id, index)]
            for index in range(len(candidates))
        ]

        model.Add(
            sum(slot_variables) <= 1
        )

    # STEP 4: Prevent overlapping maintenance blocks
    # on the same railway section.
    for i in range(len(all_candidates)):

        first = all_candidates[i]

        first_request = first['request']
        first_candidate = first['candidate']

        for j in range(i + 1, len(all_candidates)):

            second = all_candidates[j]

            second_request = second['request']
            second_candidate = second['candidate']

            # Different sections can be scheduled simultaneously.
            if (
                first_request.section_id
                != second_request.section_id
            ):
                continue

            first_start = first_candidate['start_time']
            first_end = first_candidate['end_time']

            second_start = second_candidate['start_time']
            second_end = second_candidate['end_time']

            # Check whether the two intervals overlap.
            overlaps = (
                first_start < second_end
                and second_start < first_end
            )

            if overlaps:

                first_var = variables[
                    (first_request.id, first['index'])
                ]

                second_var = variables[
                    (second_request.id, second['index'])
                ]

                model.Add(
                    first_var + second_var <= 1
                )

    # STEP 5: Define the optimization objective.
    objective_terms = []

    for item in all_candidates:

        maintenance_request = item['request']
        candidate = item['candidate']

        variable = variables[
            (maintenance_request.id, item['index'])
        ]

        priority_score = PRIORITY_WEIGHTS.get(
            maintenance_request.priority,
            40000
        )

        # Calculate difference from the preferred start time.
        if maintenance_request.preferred_start:

            difference = abs(
                int(
                    (
                        candidate['start_time']
                        - maintenance_request.preferred_start
                    ).total_seconds() // 60
                )
            )

        else:
            difference = 0

        # Higher priority and closer preferred time get better scores.
        score = priority_score - difference

        objective_terms.append(
            score * variable
        )

    model.Maximize(
        sum(objective_terms)
    )

    # STEP 6: Run Google OR-Tools solver.
    solver = cp_model.CpSolver()

    solver.parameters.max_time_in_seconds = 10

    status = solver.Solve(model)

    scheduled = []
    unscheduled = []

    # STEP 7: Collect optimized results.
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):

        for request_id, data in request_candidates.items():

            maintenance_request = data['request']
            candidates = data['candidates']

            selected_candidate = None

            for index, candidate in enumerate(candidates):

                variable = variables[
                    (request_id, index)
                ]

                if solver.Value(variable):

                    selected_candidate = candidate
                    break

            if selected_candidate:

                scheduled.append({
                    'request': maintenance_request,
                    'candidate': selected_candidate
                })

            else:

                unscheduled.append(
                    maintenance_request
                )

    else:

        unscheduled = [
            data['request']
            for data in request_candidates.values()
        ]

    # STEP 8: Return results to the Django view.
    return {
        'scheduled': scheduled,
        'unscheduled': unscheduled,
        'solver_status': solver.StatusName(status)
    }
