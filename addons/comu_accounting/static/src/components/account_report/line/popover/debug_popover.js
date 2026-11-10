import { Component } from "@odoo/owl";

export class AccountReportDebugPopover extends Component {
    static template = "comu_accounting.AccountReportDebugPopover";
    static props = {
        close: Function,
        expressionsDetail: Array,
        onClose: Function,
    };
}
