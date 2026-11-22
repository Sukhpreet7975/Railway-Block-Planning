from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('reports/', views.reports, name='reports'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # Railway Section CRUD
    path('assets/', views.assets, name='assets'),
    path('sections/', views.section_list, name='section_list'),
    path('sections/add/', views.section_create, name='section_create'),
    path('sections/edit/<int:section_id>/', views.section_update, name='section_update'),
    path('sections/delete/<int:section_id>/', views.section_delete, name='section_delete'),

    # Train Management
    path('trains/', views.train_list, name='train_list'),
    path('trains/add/', views.train_create, name='train_create'),
    path('trains/edit/<int:train_id>/', views.train_update, name='train_update'),
    path('trains/delete/<int:train_id>/', views.train_delete, name='train_delete'),

    # Train Schedules CRUD
    path('train-schedules/', views.train_schedule_list, name='train_schedule_list'),
    path('train-schedules/add/', views.train_schedule_create, name='train_schedule_create'),
    path('train-schedules/edit/<int:schedule_id>/', views.train_schedule_update, name='train_schedule_update'),
    path('train-schedules/delete/<int:schedule_id>/', views.train_schedule_delete, name='train_schedule_delete'),   

    path('section/<int:section_id>/', views.section_details, name='section_details'),
    path('request-demo/', views.request_demo, name='request_demo'),

    # Maintenance Request CRUD
    path(
        'maintenance-requests/',
        views.maintenance_request_list,
        name='maintenance_request_list'
    ),

    path(
        'maintenance-requests/add/',
        views.maintenance_request_create,
        name='maintenance_request_create'
    ),

    path(
        'maintenance-requests/edit/<int:request_id>/',
        views.maintenance_request_update,
        name='maintenance_request_update'
    ),

    path(
        'maintenance-requests/delete/<int:request_id>/',
        views.maintenance_request_delete,
        name='maintenance_request_delete'
    ),

    path(
        'ai-planner/',
        views.ai_block_planner,
        name='ai_block_planner'
    ),

    path(
        'block-plans/',
        views.block_plan_list,
        name='block_plan_list'
    ),

    path(
        'block-plans/approve/<int:plan_id>/',
        views.approve_block_plan,
        name='approve_block_plan'
    ),

    path(
        'block-plans/cancel/<int:plan_id>/',
        views.cancel_block_plan,
        name='cancel_block_plan'
    ),

    path(
        'optimize-all/',
        views.optimize_all_requests,
        name='optimize_all_requests'
    ),

    path(
        'optimize-all/save/',
        views.save_optimized_plans,
        name='save_optimized_plans'
    ),
]