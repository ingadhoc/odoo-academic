import { registry } from '@web/core/registry';

registry.category("web_tour.tours").add("filtrar_familias_con_mas_de_un_estudiante", {
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
        "trigger": ".o-dropdown-item[data-menu-xmlid='academic\\.menu_families']",
        "run": "click"
    },
    {
        "trigger": ".o_searchview_dropdown_toggler",
        "run": "click"
    },
    {
        "trigger": ".o-dropdown-item:nth-child(20)",
        "run": "click"
    },
    {
        "trigger": ".o_list_renderer",
        "run": "click"
    }
]
})
