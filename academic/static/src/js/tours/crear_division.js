import { registry } from '@web/core/registry';
import { stepUtils } from "@web_tour/tour_service/tour_utils";

registry.category("web_tour.tours").add("crear_division", {
    url: "/odoo",
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
        "trigger": ".o-dropdown-item[data-menu-xmlid='academic\\.menu_divisions']",
        "run": "click"
    },
    {
        "trigger": ".o_list_button_add",
        "run": "click"
    },
    {
        "trigger": ".o_form_button_save",
        "run": "click"
    }
]
})
