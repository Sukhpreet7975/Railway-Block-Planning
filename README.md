# AI-Powered Automatic Block Planning to Maximize Asset Availability for Train Operations on Indian Railways

> **Academic project prototype** --- A Django-based platform for
> analysing train schedules, identifying feasible maintenance windows,
> and supporting railway maintenance block planning.

![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python)
![Django](https://img.shields.io/badge/Django-Backend-092E20?logo=django)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5-7952B3?logo=bootstrap)
![SQLite](https://img.shields.io/badge/Database-SQLite-003B57?logo=sqlite)
![Status](https://img.shields.io/badge/Status-Academic%20Prototype-orange)

## Table of Contents

1.  [Project Overview](#project-overview)
2.  [Problem Statement](#problem-statement)
3.  [Objectives](#objectives)
4.  [Novelty and Key Contribution](#novelty-and-key-contribution)
5.  [Features and Functionality](#features-and-functionality)
6.  [Scheduling Engine](#scheduling-engine)
7.  [User Roles](#user-roles)
8.  [Technology Stack](#technology-stack)
9.  [Project Structure](#project-structure)
10. [Database Design](#database-design)
11. [Installation](#installation)
12. [Configuration](#configuration)
13. [Running the Application](#running-the-application)
14. [Sample Data](#sample-data)
15. [Application Workflow](#application-workflow)
16. [Security](#security)
17. [Development Roadmap](#development-roadmap)
18. [Testing Checklist](#testing-checklist)
19. [Limitations](#limitations)
20. [Future Enhancements](#future-enhancements)
21. [Disclaimer](#disclaimer)
22. [Project Information](#project-information)

------------------------------------------------------------------------

## Project Overview

Railway maintenance is essential for safe and reliable infrastructure.
Maintenance activities such as track repair, signal maintenance, and
electrical inspection must be planned around train movements. Finding a
suitable time window manually can be difficult, especially when several
schedules and maintenance requests must be considered.

This project proposes a web-based **Railway Maintenance Block Planning
System**. It brings railway sections, train schedules, maintenance
requests, proposed block plans, and planning reports together in one
platform.

The system analyses train schedule intervals for a selected railway
section, identifies free time windows, and recommends windows that can
accommodate the requested maintenance duration. Its goal is to support
more organised, consistent, and data-informed maintenance planning.

## Problem Statement

Manual or disconnected maintenance planning processes can make it
difficult to:

-   Find a time window long enough for a maintenance task.
-   Check train schedules for possible conflicts.
-   Consider existing proposed or approved maintenance blocks.
-   Prioritise urgent maintenance requests.
-   Track requests and block-plan statuses centrally.
-   Understand the relationship between planned downtime and asset
    availability.

The proposed system addresses these challenges through a centralised web
application and an automated scheduling process based on the data
entered into the system.

## Objectives

-   Maintain railway section and train information.
-   Store train schedules against railway sections.
-   Allow authorised users to submit and manage maintenance requests.
-   Detect occupied time intervals from train schedules.
-   Calculate free windows for maintenance activities.
-   Recommend feasible windows based on duration and preferred timing.
-   Store and track proposed maintenance block plans.
-   Support role-based access and administrative review.
-   Present planning information through dashboards and reports.
-   Provide a foundation for multi-request optimisation.

## Novelty and Key Contribution

### Main novelty

The central contribution is the **integration of train-schedule conflict
detection, maintenance-window identification, and preference-aware
maintenance block recommendations in one web-based planning workflow**.

Rather than merely recording maintenance requests, the system analyses
the stored schedule data to help identify when maintenance work may fit
into available time.

### Key contributions

1.  **Schedule-aware planning:** Uses train schedule intervals for the
    selected railway section to identify occupied periods.
2.  **Automatic conflict detection:** Treats train-occupied intervals
    and applicable existing block plans as unavailable time.
3.  **Maintenance-window recommendations:** Finds free intervals and
    checks whether the requested work duration fits.
4.  **Preference-aware ranking:** Ranks feasible recommendations using
    the requested preferred start time and scheduling window.
5.  **Priority-aware request management:** Records Critical, High,
    Medium, and Low priorities for planning and review.
6.  **Centralised workflow:** Connects railway sections, trains,
    schedules, maintenance requests, and block plans.
7.  **Availability-oriented reporting:** Provides a basis for analysing
    planned downtime and asset availability.

The distinctive contribution is this particular integration and
implementation. The project does not claim that railway block planning
or automated railway scheduling is itself a new concept.

> **Technical accuracy:** The single-request planner is a rule-based
> scheduling engine, not a trained machine-learning model. Describe it
> as automated or intelligent scheduling. Claim AI-based multi-request
> optimisation only after that feature has been implemented and tested.

## Features and Functionality

The following table describes the project modules. Confirm each module
against the current code before claiming it as completed.

  -----------------------------------------------------------------------
  Module                              Functionality
  ----------------------------------- -----------------------------------
  Dashboard                           Summarises sections, trains,
                                      requests, plans, and planning
                                      indicators.

  Railway section management          Creates, views, updates, and
                                      deletes section records.

  Train management                    Maintains train numbers and names.

  Train schedule management           Stores train movement intervals
                                      against sections.

  Maintenance requests                Records work type, description,
                                      duration, priority, preferred
                                      start, and status.

  Automated block planner             Analyses occupied intervals and
                                      recommends feasible maintenance
                                      windows.

  Saved block plans                   Stores and displays proposed plans
                                      and their statuses.

  Approval workflow                   Supports review and status changes
                                      when approval actions are enabled.

  Multiple-request optimiser          Intended to optimise several
                                      requests together, subject to
                                      implementation and testing.

  Reports                             Presents maintenance requests,
                                      block plans, and
                                      availability-related information.

  Authentication and roles            Restricts protected pages and
                                      management actions to authorised
                                      users.
  -----------------------------------------------------------------------

### Maintenance work categories

-   Track Repair
-   Signal Maintenance
-   Electrical Inspection
-   Track Inspection
-   Other

### Request priorities

-   Critical
-   High
-   Medium
-   Low

### Example railway sections

Illustrative development data may include Ludhiana--Jalandhar,
Jalandhar--Amritsar, and Ludhiana--Ambala. These are sample records, not
live operational railway data.

## Scheduling Engine

The single-request scheduling process uses time intervals:

1.  The planner selects a maintenance request and planning date.
2.  The system defines a planning window (the example implementation
    uses 07:00--22:00).
3.  Train schedules overlapping that window are retrieved for the
    selected section.
4.  Train movements and applicable existing proposed or approved block
    plans are collected as occupied intervals.
5.  Overlapping occupied intervals are merged.
6.  The gaps between occupied intervals are calculated as free windows.
7.  Each free window is checked against the requested maintenance
    duration.
8.  Feasible windows are ranked by their difference from the preferred
    start time, with earlier times used as a tie-breaker.
9.  The planner reviews a recommendation and saves a proposed plan if
    the save workflow is enabled.

### Simplified example

Suppose a section has these illustrative train-occupied intervals:

  Occupied interval   Status
  ------------------- ----------
  08:00--08:45        Occupied
  09:00--09:40        Occupied
  11:00--12:00        Occupied

For a planning window of 07:00--22:00, the free windows are:

-   07:00--08:00
-   08:45--09:00
-   09:40--11:00
-   12:00--22:00

A 60-minute maintenance task cannot fit into the 15-minute gap, but may
fit into the other sufficiently long gaps. Actual recommendations depend
on the data and rules in the running application.

## User Roles

  -----------------------------------------------------------------------
  Role                                Intended permissions
  ----------------------------------- -----------------------------------
  Administrator                       Manage railway sections, trains,
                                      schedules, and maintenance records;
                                      review and manage plans.

  Planner                             View planning data, submit
                                      maintenance requests, and use
                                      permitted planning features.

  Visitor                             Access only pages intentionally
                                      made public.
  -----------------------------------------------------------------------

Permissions are enforced by the application's Django views and role
decorators. A Django superuser may bypass custom role checks where
configured. Access to Django Admin separately requires appropriate staff
permissions.

## Technology Stack

  -----------------------------------------------------------------------
  Technology                          Purpose
  ----------------------------------- -----------------------------------
  Python                              Programming language and scheduling
                                      logic

  Django                              Backend, routing, authentication,
                                      ORM, and forms

  Django Templates                    Server-rendered frontend

  HTML5, CSS3                         Structure and styling

  JavaScript                          Client-side interactions

  Bootstrap 5                         Responsive interface

  Bootstrap Icons                     Interface icons

  SQLite                              Development database

  Chart.js                            Dashboard visualisations, where
                                      configured

  Google OR-Tools                     Optional/future constraint-based
                                      multi-request optimisation

  Visual Studio Code                  Development environment

  Git and GitHub                      Version control and hosting
  -----------------------------------------------------------------------

## Project Structure

The project is organised as a Django project with an `operations`
application. The exact files may vary as development continues.

``` text
RailwayBlockPlanning/
├── manage.py
├── db.sqlite3
├── requirements.txt
├── railway_project/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── operations/
│   ├── migrations/
│   ├── services/
│   │   ├── __init__.py
│   │   ├── block_planner.py
│   │   └── multi_request_optimizer.py
│   ├── admin.py
│   ├── apps.py
│   ├── decorators.py
│   ├── forms.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── templates/
│   ├── operations/
│   │   ├── base.html
│   │   ├── home.html
│   │   ├── dashboard.html
│   │   ├── about.html
│   │   ├── ai_block_planner.html
│   │   ├── block_plan_list.html
│   │   └── reports.html
│   └── registration/
│       └── login.html
└── static/
    └── css/
        └── style.css
```

Remove any paths from this tree that do not exist in your final
repository.

## Database Design

### RailwaySection

Stores section information:

-   `section_code`
-   `name`
-   `from_station`
-   `to_station`
-   `distance_km`
-   `is_active`

### Train

Stores train identification:

-   `train_number`
-   `train_name`

### TrainSchedule

Connects a train to a railway section and stores its scheduled interval:

-   `train`
-   `section`
-   `start_time`
-   `end_time`
-   `direction`

### MaintenanceRequest

Stores maintenance work:

-   `section`
-   `work_type`
-   `description`
-   `duration_minutes`
-   `priority`
-   `preferred_start`
-   `status`
-   `created_at`

### BlockPlan

Stores a planned maintenance block:

-   `maintenance_request`
-   `start_time`
-   `end_time`
-   `status`
-   `created_at`

Typical plan statuses include Proposed, Approved, Cancelled, and
Completed. Check `operations/models.py` for the exact relationships and
choices in your version.

## Installation

### Prerequisites

-   Python 3
-   pip
-   Visual Studio Code (recommended)
-   Git (optional)

### 1. Clone the repository

Replace the placeholder URL with your GitHub repository URL:

``` bash
git clone https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
cd RailwayBlockPlanning
```

Alternatively, open your existing project folder in VS Code.

### 2. Create and activate a virtual environment

**Windows Command Prompt:**

``` bat
python -m venv venv
venv\Scripts\activate.bat
```

**Windows PowerShell:**

``` powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, use Command Prompt or follow your
organisation's approved PowerShell execution-policy guidance.

### 3. Install dependencies

If `requirements.txt` is available:

``` bash
python -m pip install -r requirements.txt
```

If it has not yet been created:

``` bash
python -m pip install django
```

Install optional packages only when the related code uses them. For
example, if the optimiser imports OR-Tools:

``` bash
python -m pip install ortools
```

### 4. Apply migrations

``` bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create an administrator

``` bash
python manage.py createsuperuser
```

Follow the prompts to create the account.

### 6. Start the development server

``` bash
python manage.py runserver
```

Open the application at http://127.0.0.1:8000/.

## Configuration

### Django settings

Check `railway_project/settings.py` and ensure:

-   `operations` is included in `INSTALLED_APPS`.
-   The project templates directory is configured.
-   Static files are configured.
-   Database settings are correct.
-   Login and logout redirects point to valid routes.

Typical development settings include:

``` python
INSTALLED_APPS = [
    # Django default applications...
    'operations',
]

# Inside the existing TEMPLATES configuration:
'DIRS': [BASE_DIR / 'templates'],

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/accounts/login/'
```

Keep the rest of Django's generated `TEMPLATES` configuration; the
snippet above is not a complete replacement for it.

### URL configuration

The project URL configuration should include Django Admin, built-in
authentication URLs, and application URLs:

``` python
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', include('operations.urls')),
]
```

### Configure application roles

If the application uses the `Admin` and `Planner` groups:

1.  Log in to Django Admin using a superuser.
2.  Open **Authentication and Authorization → Groups**.
3.  Create groups named `Admin` and `Planner`.
4.  Add the appropriate users to each group.
5.  Enable staff access separately for users who need the Django Admin
    site.

Group names must match those checked by the application's decorators.

## Running the Application

1.  Activate the virtual environment.
2.  Open a terminal in the folder containing `manage.py`.
3.  Apply migrations if models have changed.
4.  Run `python manage.py runserver`.
5.  Visit http://127.0.0.1:8000/.
6.  Log in using an authorised account.

Stop the development server with `CTRL + C`.

Useful routes in the current project design:

  Page                   Local URL
  ---------------------- --------------------------
  Home                   `/`
  Dashboard              `/dashboard/`
  Login                  `/accounts/login/`
  Railway sections       `/sections/`
  Trains                 `/trains/`
  Train schedules        `/train-schedules/`
  Maintenance requests   `/maintenance-requests/`
  AI block planner       `/ai-planner/`
  Saved block plans      `/block-plans/`
  Reports                `/reports/`
  Django Admin           `/admin/`

Routes may differ if your `operations/urls.py` has been changed.

## Sample Data

Illustrative development data may include:

  Section code   Route                     Example distance
  -------------- ----------------------- ------------------
  SEC001         Ludhiana -- Jalandhar                60 km
  SEC002         Jalandhar -- Amritsar                80 km
  SEC003         Ludhiana -- Ambala                  110 km

Example train records:

-   12029 --- Swarna Shatabdi Express
-   12030 --- New Delhi Shatabdi Express
-   12459 --- New Delhi Amritsar Express
-   14631 --- Dehradun Amritsar Express
-   12925 --- Paschim Express

Example maintenance requests can cover track repair, signal maintenance,
electrical inspection, and track inspection, with different durations
and priorities.

All sample records are for software testing and demonstration. They are
not verified timetables or live railway information.

## Application Workflow

``` text
Authorised user logs in
          |
          v
Selects or creates a maintenance request
          |
          v
Selects a railway section and planning date
          |
          v
System retrieves train schedules
          |
          v
Occupied intervals are identified and merged
          |
          v
Free maintenance windows are calculated
          |
          v
Feasible windows are ranked and displayed
          |
          v
Planner reviews a recommendation
          |
          v
Proposed block plan is saved
          |
          v
Authorised administrator reviews the plan
          |
          v
Plan status and reports are updated
```

This represents the intended workflow. Verify each step in the running
application before describing it as completed.

## Security

The application uses or is designed to use:

-   Django authentication for login and logout.
-   CSRF tokens in POST forms.
-   Role-based view protection through custom decorators.
-   Django ORM for database access.
-   ModelForms for structured data entry.
-   Form validation for relevant date and time fields.
-   Protected database relationships where configured.

Before production deployment, additional work is required: secure secret
management, HTTPS, production database configuration, logging, backups,
deployment hardening, and a complete permissions review.

## Development Roadmap

  -----------------------------------------------------------------------
  Stage                               Work
  ----------------------------------- -----------------------------------
  1                                   Django environment and project
                                      setup

  2                                   Application structure, views, and
                                      URLs

  3                                   Templates and dashboard interface

  4                                   Database models and migrations

  5                                   CRUD for sections, trains,
                                      schedules, and requests

  6                                   Authentication and role-based
                                      access

  7                                   Single-request maintenance-window
                                      recommendation engine

  8                                   Saving and displaying block plans

  9                                   Approval and cancellation workflow

  10                                  Multi-request optimisation with
                                      resource and priority constraints

  11                                  Availability analytics and reports

  12                                  Testing, documentation, and
                                      demonstration
  -----------------------------------------------------------------------

Before publishing, mark each item as **Completed**, **In Progress**, or
**Planned** according to the actual state of the code.

## Testing Checklist

### Application basics

-   [ ] Application starts without errors.
-   [ ] Home, login, and dashboard pages load.
-   [ ] Static assets load correctly.
-   [ ] Unauthenticated users are redirected from protected pages.

### Data management

-   [ ] Permitted users can manage railway sections.
-   [ ] Permitted users can manage trains and schedules.
-   [ ] Invalid schedule intervals are rejected.
-   [ ] Maintenance requests can be submitted and viewed.
-   [ ] Required fields and invalid values are validated.

### Scheduling

-   [ ] Schedules for the selected section are retrieved.
-   [ ] Overlapping train intervals are merged correctly.
-   [ ] Free windows are calculated correctly.
-   [ ] A task cannot be placed in a window shorter than its duration.
-   [ ] Existing active block plans are treated as occupied.
-   [ ] Cancelled plans are excluded from occupied intervals.
-   [ ] Recommendations are ranked consistently.
-   [ ] A recommendation is revalidated before saving.

### Permissions and reports

-   [ ] Planner and administrator permissions are tested separately.
-   [ ] Unauthorised users cannot perform restricted actions.
-   [ ] Approval and cancellation actions accept only valid POST
    requests.
-   [ ] Dashboard totals match database records.
-   [ ] Report totals and availability calculations are checked against
    test data.

## Limitations

-   The application is an academic prototype and uses illustrative data.
-   Recommendation quality depends on the completeness and correctness
    of stored schedules and maintenance records.
-   The basic single-request engine is rule-based and is not a trained
    machine-learning model.
-   A free interval in the stored timetable does not prove that a real
    railway block is safe or operationally permissible.
-   Real railway operations involve additional constraints such as
    possessions, line capacity, direction, speed restrictions, crew and
    equipment availability, safety margins, and formal approvals. These
    are outside the basic model unless explicitly implemented.
-   Availability metrics require a clearly defined numerator,
    denominator, time period, and treatment of planned versus unplanned
    downtime.
-   Multi-request optimisation and resource constraints must be
    implemented and tested before being claimed as working capabilities.

## Future Enhancements

1.  **Constraint-based multi-request optimisation:** Use Google OR-Tools
    to schedule several requests while considering priorities,
    durations, resources, and time constraints.
2.  **Additional operational constraints:** Model safety buffers, crew
    availability, equipment availability, and section-specific
    restrictions.
3.  **Availability analytics:** Calculate availability over configurable
    periods and distinguish planned maintenance from unexpected
    downtime.
4.  **Interactive timeline:** Visualise train movements, occupied
    intervals, and proposed maintenance windows.
5.  **Audit trail:** Record who created, modified, approved, or
    cancelled each plan and when.
6.  **Notifications:** Notify planners and administrators when requests
    or plans change status.
7.  **Data import and export:** Support controlled CSV or Excel
    import/export for demonstration datasets and reports.
8.  **Automated tests:** Add unit tests for interval merging,
    free-window generation, conflict checks, permissions, and
    optimisation.
9.  **Production deployment:** Use a production database, secure
    hosting, HTTPS, monitoring, and backups.
10. **Authorised data integration:** Consider external railway data
    sources only after formal access, validation, and safety review.

## Disclaimer

This software is an **academic demonstration prototype** developed for
educational and research purposes.

It uses illustrative data and simplified scheduling assumptions. It is
not connected to Indian Railways' live operational systems and must not
be used to issue, approve, or execute real railway maintenance blocks or
make safety-critical decisions.

All real railway maintenance and block decisions must follow applicable
railway rules, approved procedures, and the authority of qualified
railway personnel.

## Project Information

**Project Title:** AI-Powered Automatic Block Planning to Maximize Asset
Availability for Train Operations on Indian Railways

**Developer:** Add your name\
**Institution:** Add your institution\
**Department:** Add your department\
**Academic Year:** Add your academic year

Developed as an academic project using Python, Django, and web
technologies.

------------------------------------------------------------------------

## License

Add a license before distributing this repository publicly. Without a
license, normal copyright restrictions apply and reuse is not
automatically permitted.
