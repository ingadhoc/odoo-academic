{
    "name": "Academic HR",
<<<<<<< ea1600afb14e811657cfce2c8910b924e066a408
    "version": "19.0.1.2.0",
||||||| 4bf47b4a3654206a0bc23e9e1aa21a62e68cdf3d
    "version": "18.0.1.2.0",
=======
    "version": "18.0.1.3.0",
>>>>>>> c4b10c3eb62b062c84a419614bc48891b73c4282
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
        "hr_attendance",
    ],
    "data": [
        "security/academic_hr_security.xml",
        "security/ir.model.access.csv",
        "views/hr_leave_views.xml",
        "views/hr_timesheet_views.xml",
        "views/hr_employee_views.xml",
        "views/hr_leave_allocation_views.xml",
        "views/hr_attendance_views.xml",
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
