import { registry } from '@web/core/registry';

registry.category("web_tour.tours").add("crear_Estudiante", {
    url: "/odoo?debug=1",
    steps: () => [
    {
        "trigger": ".o_app[data-menu-xmlid='academic\\.menu_academic']",
        "run": "click"
    },
    {
        "trigger": ".o-dropdown[data-menu-xmlid='academic\\.menu_partners']",
        "run": "click"
    },
    {
        "trigger": ".o-dropdown-item[data-menu-xmlid='academic\\.menu_students']",
        "run": "click"
    },
    {
        "trigger": ".o_list_button_add",
        "run": "click"
    },
    {
        "trigger": ".o_notebook_headers li:nth-child(4) > a",
        "run": "click"
    },
    {
        "trigger": ".o_notebook_headers li:nth-child(2) > a",
        "run": "click"
    },
    {
        "trigger": ".o_notebook_headers li:nth-child(1) > a",
        "run": "click"
    }
]
})
