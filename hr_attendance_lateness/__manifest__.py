{
    "name": "HR Attendance Lateness",
    "version": "18.0.1.0.0",
    "category": "Human Resources/Attendances",
    "license": "AGPL-3",
    "summary": "Track employee lateness by comparing check-in times against scheduled hours",
    "author": "ADHOC SA",
    "website": "https://www.adhoc.inc",
    "depends": [
        "hr_attendance",
    ],
    "data": [
        "views/hr_attendance_views.xml",
        "views/res_config_settings_views.xml",
    ],
    "installable": False,
    "auto_install": False,
    "application": False,
}
