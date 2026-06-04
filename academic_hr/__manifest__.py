{
    "name": "Academic HR",
    "version": "18.0.1.3.0",
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
        "portal",
    ],
    "data": [
        "security/academic_hr_security.xml",
        "security/ir.model.access.csv",
        "views/hr_leave_views.xml",
        "views/hr_timesheet_views.xml",
        "views/hr_employee_views.xml",
        "views/hr_leave_allocation_views.xml",
        "views/portal_templates.xml",
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
