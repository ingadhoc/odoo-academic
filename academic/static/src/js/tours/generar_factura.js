import { registry } from '@web/core/registry';

registry.category("web_tour.tours").add("generar_factura", {
    url: "/odoo?debug=1",
    steps: () => [
    {
        "trigger": ".o_app[data-menu-xmlid='sale_subscription\\.menu_sale_subscription_root']",
        "run": "click"
    },
    {
        "trigger": ".o_data_row:nth-child(2) > .o_data_cell[name='partner_id']",
        "run": "click"
    },
    {
        "trigger": ".o_statusbar_buttons > button[name='\\34 35']",
        "run": "click"
    },
    {
        "trigger": ".o_technical_modal button[name='create_invoices']",
        "run": "click"
    },
    {
        "trigger": ".o_statusbar_buttons > button[name='action_post']",
        "run": "click"
    },
    {
        "trigger": ".o_back_button > a",
        "run": "click"
    },
    {
        "trigger": ".o_menu_toggle",
        "run": "click"
    },
    {
        "trigger": ".o_app[data-menu-xmlid='accountant\\.menu_accounting']",
        "run": "click"
    },
    {
        "trigger": ".o-dropdown[data-menu-xmlid='account\\.menu_finance_receivables']",
        "run": "click"
    },
    {
        "trigger": ".o-dropdown-item[data-menu-xmlid='account\\.menu_action_move_out_invoice_type']",
        "run": "click"
    },
    {
        "trigger": ".o_data_row:nth-child(1) > .o_data_cell[name='name']",
        "run": "click"
    }
]
})
