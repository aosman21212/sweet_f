/** @odoo-module **/

import { Component, useState, onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";

export class SweetFactoryDashboard extends Component {
    static template = "sweet_factory_management.Dashboard";
    static props = {};

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");

        this.state = useState({
            stats: null,
            loading: true,
        });

        onWillStart(async () => {
            await this._loadData();
        });
    }

    async _loadData() {
        this.state.loading = true;
        this.state.stats = await this.orm.call("sweet.dashboard", "get_dashboard_data", []);
        this.state.loading = false;
    }

    // ── Navigation helpers ──────────────────────────────────

    openBatches(extraDomain) {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: _t("Production Batches"),
            res_model: "sweet.batch",
            views: [[false, "list"], [false, "form"]],
            domain: extraDomain || [],
        });
    }

    openRecipes(extraDomain) {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: _t("Recipes"),
            res_model: "sweet.recipe",
            views: [[false, "list"], [false, "form"]],
            domain: extraDomain || [],
        });
    }

    openQC(extraDomain) {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: _t("Quality Checks"),
            res_model: "sweet.quality.check",
            views: [[false, "list"], [false, "form"]],
            domain: extraDomain || [],
        });
    }

    openMachines(extraDomain) {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: _t("Machines"),
            res_model: "sweet.machine",
            views: [[false, "list"], [false, "form"]],
            domain: extraDomain || [],
        });
    }

    openBatch(id) {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: _t("Batch"),
            res_model: "sweet.batch",
            views: [[false, "form"]],
            res_id: id,
        });
    }

    // ── Label helpers ──────────────────────────────────────

    stateLabel(state) {
        const labels = {
            draft:         _t("Draft"),
            confirmed:     _t("Confirmed"),
            in_progress:   _t("In Production"),
            quality_check: _t("QC Check"),
            done:          _t("Done"),
            failed:        _t("Failed"),
            cancelled:     _t("Cancelled"),
        };
        return labels[state] || state;
    }
}

registry.category("actions").add("sweet_factory_dashboard", SweetFactoryDashboard);
