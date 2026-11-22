
from datetime import date, datetime, time

from django.test import TestCase
from django.utils import timezone

from operations.models import (
    RailwaySection,
    MaintenanceRequest,
    BlockPlan,
)

from operations.services.analytics import (
    get_dashboard_analytics,
    merge_intervals,
)


class DashboardAnalyticsTests(TestCase):

    def setUp(self):

        self.planning_date = date(2026, 11, 1)

        self.section = RailwaySection.objects.create(
            section_code='TEST001',
            name='Test Railway Section',
            from_station='Station A',
            to_station='Station B',
            distance_km=50,
            is_active=True,
        )

        self.maintenance_request = MaintenanceRequest.objects.create(
            section=self.section,
            work_type='TRACK_REPAIR',
            description='Test track maintenance',
            duration_minutes=60,
            priority='HIGH',
            status='PLANNED',
        )

    def make_datetime(self, hour, minute=0):

        return timezone.make_aware(
            datetime.combine(
                self.planning_date,
                time(hour, minute)
            )
        )

    def test_availability_without_block_plans(self):

        result = get_dashboard_analytics(
            self.planning_date
        )

        self.assertEqual(
            result['availability_percent'],
            100.0
        )

        self.assertEqual(
            result['total_blocked_hours'],
            0
        )

    def test_proposed_plan_reduces_availability(self):

        BlockPlan.objects.create(
            maintenance_request=self.maintenance_request,
            start_time=self.make_datetime(8),
            end_time=self.make_datetime(9),
            status='PROPOSED',
        )

        result = get_dashboard_analytics(
            self.planning_date
        )

        self.assertEqual(
            result['availability_percent'],
            93.33
        )

        self.assertEqual(
            result['total_blocked_hours'],
            1.0
        )

        self.assertEqual(
            result['proposed_plans'],
            1
        )

    def test_approved_plan_counts_as_blocked_time(self):

        BlockPlan.objects.create(
            maintenance_request=self.maintenance_request,
            start_time=self.make_datetime(8),
            end_time=self.make_datetime(10),
            status='APPROVED',
        )

        result = get_dashboard_analytics(
            self.planning_date
        )

        self.assertEqual(
            result['approved_plans'],
            1
        )

        self.assertEqual(
            result['total_blocked_hours'],
            2.0
        )

    def test_cancelled_plan_does_not_reduce_availability(self):

        BlockPlan.objects.create(
            maintenance_request=self.maintenance_request,
            start_time=self.make_datetime(8),
            end_time=self.make_datetime(9),
            status='CANCELLED',
        )

        result = get_dashboard_analytics(
            self.planning_date
        )

        self.assertEqual(
            result['availability_percent'],
            100.0
        )

        self.assertEqual(
            result['total_blocked_hours'],
            0
        )

    def test_overlapping_intervals_are_merged(self):

        intervals = [
            (
                self.make_datetime(8),
                self.make_datetime(9),
            ),
            (
                self.make_datetime(8, 30),
                self.make_datetime(9, 30),
            ),
            (
                self.make_datetime(11),
                self.make_datetime(12),
            ),
        ]

        merged = merge_intervals(intervals)

        self.assertEqual(len(merged), 2)

        self.assertEqual(
            merged[0],
            (
                self.make_datetime(8),
                self.make_datetime(9, 30),
            )
        )

        self.assertEqual(
            merged[1],
            (
                self.make_datetime(11),
                self.make_datetime(12),
            )
        )

    def test_inactive_section_is_not_counted(self):

        self.section.is_active = False
        self.section.save()

        result = get_dashboard_analytics(
            self.planning_date
        )

        self.assertEqual(
            result['total_sections'],
            0
        )

        self.assertEqual(
            result['availability_percent'],
            0
        )
