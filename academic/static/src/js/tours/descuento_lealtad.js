import { registry } from '@web/core/registry';

registry.category("web_tour.tours").add("descuento_lealtad", {
    url: "/odoo?debug=1",
    steps: () => [
    {
        "trigger": ".o_app[data-menu-xmlid='sale\\.sale_menu_root']",
        "run": "click"
    },
    {
        "trigger": ".o-dropdown[data-menu-xmlid='sale\\.product_menu_catalog']",
        "run": "click"
    },
    {
        "trigger": ".o-dropdown-item[data-menu-xmlid='sale_loyalty\\.menu_discount_loyalty_type_config']",
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
        "trigger": ".o_field_widget[name='program_type'] > .o_input",
        "run": "click"
    },
    {
        "trigger": ".o_form_sheet > .o_group > .o_inner_group:nth-child(2)",
        "run": "drag_and_drop .o_inner_group:nth-child(2) > .o_wrap_field:nth-child(3) sup"
    },
    {
        "trigger": ".o_field_domain_dialog_button",
        "run": "click"
    },
    {
        "trigger": ".o_tree_editor_row:nth-child(2) > a",
        "run": "click"
    },
    {
        "trigger": ".o_model_field_selector_value",
        "run": "click"
    },
    {
        "trigger": ".o_model_field_selector_popover_search > .o_input",
        "run": "edit clien"
    },
    {
        "trigger": ".o_model_field_selector_popover_item:nth-child(1) > .o_model_field_selector_popover_item_relation",
        "run": "click"
    },
    {
        "trigger": ".o_model_field_selector_popover_search > .o_input",
        "run": "edit etique"
    },
    {
        "trigger": ".o_model_field_selector_popover_item_name",
        "run": "click"
    },
    {
        "trigger": ".o_tree_editor_editor:nth-child(2) > .o_input",
        "run": "click"
    },
    {
        "trigger": ".o_input .o-autocomplete--input",
        "run": "edit 8"
    },
    {
        "trigger": ".o_domain_selector_debug_container > textarea",
        "run": "click"
    },
    {
        "trigger": ".o_input .o-autocomplete--input",
        "run": "click"
    },
    {
        "trigger": ".o-autocomplete--dropdown-item:nth-child(9) > a",
        "run": "click"
    },
    {
        "trigger": ".o_data_row:nth-child(9) input",
        "run": "click"
    },
    {
        "trigger": ".o_select_button",
        "run": "click"
    },
    {
        "trigger": ".o_technical_modal footer > button:nth-child(1)",
        "run": "click"
    },
    {
        "trigger": ".o_kanban_record:nth-child(1) > div[name='reward_info']",
        "run": "click"
    },
    {
        "trigger": ".o_field_widget[name='discount'] > .o_input",
        "run": "click"
    },
    {
        "trigger": ".o_field_widget[name='discount'] > .o_input",
        "run": "edit 10,00"
    },
    {
        "trigger": ".o_field_widget[name='description'] > .o_input",
        "run": "edit 10 % en su orden"
    },
    {
        "trigger": ".o_field_widget[name='discount_line_product_id'] .o-autocomplete--input",
        "run": "click"
    },
    {
        "trigger": ".o_form_sheet > .o_inner_group > .o_wrap_field:nth-child(1) > .o_cell:nth-child(2)",
        "run": "click"
    },
    {
        "trigger": "footer > .o_form_button_save",
        "run": "click"
    },
    {
        "trigger": ".o_form_button_save",
        "run": "click"
    }
]
})
