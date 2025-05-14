import { registry } from '@web/core/registry';

registry.category("web_tour.tours").add("etiquetas_de_cliente", {
    url: "/odoo?debug=1",
    steps: () => [
    {
        "trigger": ".o_app[data-menu-xmlid='contacts\\.menu_contacts']",
        "run": "click"
    },
    {
        "trigger": ".o-dropdown[data-menu-xmlid='contacts\\.res_partner_menu_config']",
        "run": "click"
    },
    {
        "trigger": ".o-dropdown-item[data-menu-xmlid='contacts\\.menu_partner_category_form']",
        "run": "click"
    },
    {
        "trigger": ".o_list_button_add",
        "run": "click"
    },
    {
        "trigger": ".o_field_widget[name='name'] > .o_input",
        "run": "edit Descuento por hermano 10%"
    },
    {
        "trigger": ".o_list_renderer",
        "run": "click"
    }
]
})
