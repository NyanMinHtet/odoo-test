import { Component } from "@odoo/owl";

export class AccountReportEllipsisPopover extends Component {
    static template = "comu_accounting.AccountReportEllipsisPopover";
    static props = {
        close: Function,
        name: String,
        copyEllipsisText: Function,
    };
}
