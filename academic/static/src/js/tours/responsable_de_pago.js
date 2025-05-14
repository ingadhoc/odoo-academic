import { registry } from '@web/core/registry';

registry.category("web_tour.tours").add("responsable_de_pago", {
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
        "trigger": ".o_data_row:nth-child(1) > .o_data_cell[name='complete_name']",
        "run": "click"
    },
    {
        "trigger": ".o_notebook_headers li:nth-child(2) > a",
        "run": "click"
    },
    {
        "trigger": ".o_field_x2many_list_row_add > a",
        "run": "click"
    },
    {
        "trigger": ".o_field_widget[name='partner_id'] .o-autocomplete--input",
        "run": "edit Di"
    },
    {
        "trigger": ".o-autocomplete--dropdown-item:nth-child(3) > a",
        "run": "click"
    },
    {
        "trigger": ".o_field_widget[name='relationship_id'] .o-autocomplete--input",
        "run": "click"
    },
    {
        "trigger": ".o-autocomplete--dropdown-item:nth-child(2) > a",
        "run": "click"
    },
    {
        "trigger": ".o_field_many2many_selection .o-autocomplete--input",
        "run": "click"
    },
    {
        "trigger": ".o-autocomplete--dropdown-item:nth-child(3) > a",
        "run": "click"
    },
    {
        "trigger": ".o_field_many2many_selection .o-autocomplete--input",
        "run": "drag_and_drop .o_field_many2many_selection .o-autocomplete"
    },
    {
        "trigger": ".o_form_button_save",
        "run": "click"
    }
]
})
