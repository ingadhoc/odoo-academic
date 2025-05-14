import { registry } from '@web/core/registry';

registry.category("web_tour.tours").add("crear_grupos", {
    url: "/odoo?debug=1",
    steps: () => [
    {
        "trigger": ".o_app[data-menu-xmlid='academic\\.menu_academic']",
        "run": "click"
    },
    {
        "trigger": ".o-dropdown[data-menu-xmlid='academic\\.menu_data']",
        "run": "click"
    },
    {
        "trigger": ".o-dropdown-item[data-menu-xmlid='academic\\.menu_groups']",
        "run": "click"
    },
    {
        "trigger": ".o_list_button_add",
        "run": "click"
    },
    {
        "trigger": ".o_field_widget[name='level_id'] .o-autocomplete--input",
        "run": "click"
    },
    {
        "trigger": ".o-autocomplete--dropdown-item:nth-child(1) > a",
        "run": "click"
    },
    {
        "trigger": ".o_field_widget[name='division_id'] .o-autocomplete--input",
        "run": "click"
    },
    {
        "trigger": ".o-autocomplete--dropdown-item:nth-child(1) > a",
        "run": "click"
    },
    {
        "trigger": ".o_form_button_save",
        "run": "click"
    }
]
})
