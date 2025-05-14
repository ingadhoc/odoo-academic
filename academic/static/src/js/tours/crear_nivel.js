import { registry } from '@web/core/registry';

registry.category("web_tour.tours").add("crear_nivel", {
    url: "/odoo?debug=1",
    steps: () => [
    {
        "trigger": ".o_app[data-menu-xmlid='academic\\.menu_academic']",
        "run": "click"
    },
    {
        "trigger": ".o-dropdown[data-menu-xmlid='academic\\.menu_configuration']",
        "run": "click"
    },
    {
        "trigger": ".o-dropdown-item[data-menu-xmlid='academic\\.menu_levels']",
        "run": "click"
    },
    {
        "trigger": ".o_list_button_add",
        "run": "click"
    }
]
})
