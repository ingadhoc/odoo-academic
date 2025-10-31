/** @odoo-module **/

import { registry } from "@web/core/registry";

async function doMultiPrint(env, action) {
    for (const report of action.params.reports) {
        await env.services.action.doAction({ type: "ir.actions.report", ...report });
    }
    if (action.params.anotherAction) {
        return env.services.action.doAction(action.params.anotherAction);
    }
    return false;
}

registry.category("actions").add("academic_do_multi_print", doMultiPrint);
