import { AccountReport } from "@comu_accounting/components/account_report/account_report";
import { AccountReportLine } from "@comu_accounting/components/account_report/line/line";
import { PartnerLedgerFollowupLineCell } from "@comu_accounting/components/partner_ledger_followup/line_cell/line_cell";

export class PartnerLedgerFollowupLine extends AccountReportLine {
    static template = "comu_accounting.PartnerLedgerFollowupLine";
    static components = {
        ...AccountReportLine.components,
        PartnerLedgerFollowupLineCell,
    };
}
AccountReport.registerCustomComponent(PartnerLedgerFollowupLine);
