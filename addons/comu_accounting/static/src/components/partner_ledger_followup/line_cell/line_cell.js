import { AccountReportLineCell } from "@comu_accounting/components/account_report/line_cell/line_cell";

export class PartnerLedgerFollowupLineCell extends AccountReportLineCell {
    static template = "comu_accounting.PartnerLedgerFollowupLineCell";

    async toggleNoFollowup(ev) {
        const res = await this.orm.call(
            "account.partner.ledger.report.handler",
            "action_toggle_no_followup",
            [this.props.line.id, this.controller.lines.map((line) => line.id)]
        );
        this.controller.updateLines(res.updated_line_ids, "no_followup", res.updated_value);
    }
}
