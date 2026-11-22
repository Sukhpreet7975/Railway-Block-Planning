from django.contrib import admin
from .models import (
    RailwaySection,
    Train,
    TrainSchedule,
    MaintenanceRequest,
    BlockPlan
)

@admin.register(RailwaySection)
class RailwaySectionAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'section_code',
        'name',
        'from_station',
        'to_station',
        'is_active'
    )
    search_fields = ('section_code', 'name')
    list_filter = ('is_active',)


@admin.register(Train)
class TrainAdmin(admin.ModelAdmin):
    list_display = ('id', 'train_number', 'train_name')
    search_fields = ('train_number', 'train_name')


@admin.register(TrainSchedule)
class TrainScheduleAdmin(admin.ModelAdmin):
    list_display = ('id', 'train', 'section', 'start_time', 'end_time')
    list_filter = ('section',)


@admin.register(MaintenanceRequest)
class MaintenanceRequestAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'section',
        'work_type',
        'priority',
        'duration_minutes',
        'status'
    )
    list_filter = ('priority', 'status', 'work_type')
    search_fields = ('description',)

@admin.register(BlockPlan)
class BlockPlanAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'maintenance_request',
        'start_time',
        'end_time',
        'status',
        'created_at'
    )

    list_filter = ('status',)

    search_fields = (
        'maintenance_request__description',
        'maintenance_request__section__name'
    )