{
    "name": "Academic HR",
    "version": "19.0.1.0.0",
    "category": "Human Resources",
    "summary": "HR extensions for academic institutions with multiple employee support",
    "author": "ADHOC SA",
    "website": "https://www.adhoc.inc",
    "license": "AGPL-3",
    "depends": [
        "academic",
        "hr_holidays",
        "hr_timesheet",
        "timesheet_grid",
    ],
    "data": [
        "views/hr_leave_views.xml",
        "views/hr_timesheet_views.xml",
        "views/hr_employee_views.xml",
        "views/hr_leave_allocation_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "academic_hr/static/src/css/ribbon.css",
        ],
    },
    "installable": True,
    "auto_install": False,
    "application": False,
}
