import { registry } from '@web/core/registry';

registry.category("web_tour.tours").add("etiqueta_alumno", {
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
        "trigger": ".o_kanban_record:nth-child(6) > main > div",
        "run": "click"
    },
    {
        "trigger": ".o_field_widget[name='company_id'] .o-autocomplete--input",
        "run": "click"
    },
    {
        "trigger": ".o-autocomplete--dropdown-item:nth-child(1) > a",
        "run": "click"
    },
    {
        "trigger": ".o_form_sheet > .o_group > .o_inner_group:nth-child(2)",
        "run": "drag_and_drop .o_wrap_field:nth-child(5) > .o_cell:nth-child(1) sup"
    },
    {
        "trigger": ".o_field_many2many_selection .o-autocomplete--input",
        "run": "click"
    },
    {
        "trigger": ".o-autocomplete--dropdown-item:nth-child(2) > a",
        "run": "click"
    },
    {
        "trigger": ".o_form_button_save",
        "run": "click"
    }
]
})
