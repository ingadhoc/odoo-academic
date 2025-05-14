import { registry } from '@web/core/registry';

registry.category("web_tour.tours").add("crear_plan_de_estudios", {
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
        "trigger": ".o-dropdown-item[data-menu-xmlid='academic\\.menu_study_plan']",
        "run": "click"
    },
    {
        "trigger": ".o_list_button_add",
        "run": "click"
    },
    {
        "trigger": ".o_input",
        "run": "edit Primario"
    },
    {
        "trigger": ".o_field_x2many_list_row_add > a",
        "run": "click"
    },
    {
        "trigger": ".o_data_row:nth-child(1) .o-checkbox",
        "run": "click"
    },
    {
        "trigger": ".o_select_button",
        "run": "click"
    },
    {
        "trigger": ".o_form_button_save",
        "run": "click"
    }
]
})
