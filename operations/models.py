from django.db import models


# 1. Railway Section Model
class RailwaySection(models.Model):

    section_code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    from_station = models.CharField(max_length=100)
    to_station = models.CharField(max_length=100)
    distance_km = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True
    )
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.section_code} - {self.name}"


# 2. Train Model
class Train(models.Model):

    train_number = models.CharField(max_length=20, unique=True)
    train_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.train_number} - {self.train_name}"


# 3. Train Schedule Model
class TrainSchedule(models.Model):

    train = models.ForeignKey(
        Train,
        on_delete=models.PROTECT,
        related_name='schedules'
    )

    section = models.ForeignKey(
        RailwaySection,
        on_delete=models.PROTECT,
        related_name='train_schedules'
    )

    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    direction = models.CharField(
        max_length=50,
        blank=True
    )

    def __str__(self):
        return f"{self.train} - {self.section}"


# 4. Maintenance Request Model
class MaintenanceRequest(models.Model):

    WORK_TYPES = [
        ('TRACK_REPAIR', 'Track Repair'),
        ('SIGNAL', 'Signal Maintenance'),
        ('ELECTRICAL', 'Electrical Inspection'),
        ('TRACK_INSPECTION', 'Track Inspection'),
        ('OTHER', 'Other'),
    ]

    PRIORITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    ]

    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PLANNED', 'Planned'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]

    section = models.ForeignKey(
        RailwaySection,
        on_delete=models.PROTECT,
        related_name='maintenance_requests'
    )

    work_type = models.CharField(
        max_length=30,
        choices=WORK_TYPES
    )

    description = models.TextField()

    duration_minutes = models.PositiveIntegerField()

    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='MEDIUM'
    )

    preferred_start = models.DateTimeField(
        null=True,
        blank=True
    )

    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='PENDING'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Request #{self.id} - {self.section}"


class BlockPlan(models.Model):

    STATUS_CHOICES = [
        ('PROPOSED', 'Proposed'),
        ('APPROVED', 'Approved'),
        ('CANCELLED', 'Cancelled'),
        ('COMPLETED', 'Completed'),
    ]

    maintenance_request = models.ForeignKey(
        MaintenanceRequest,
        on_delete=models.PROTECT,
        related_name='block_plan'
    )

    start_time = models.DateTimeField()

    end_time = models.DateTimeField()

    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='PROPOSED'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return (
            f"Block Plan #{self.id} - "
            f"{self.maintenance_request.section}"
        )

    class Meta:
        ordering = ['start_time']
