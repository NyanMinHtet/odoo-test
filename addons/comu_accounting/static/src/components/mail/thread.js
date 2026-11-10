import { Thread } from "@mail/core/common/thread";
import { AccountReportMessage } from "./message";

export class AccountReportThread extends Thread {
    static template = "comu_accounting.Thread";
    static props = [...Thread.props, "reportController?"];
    static components = { ...Thread.components, Message: AccountReportMessage };
}
