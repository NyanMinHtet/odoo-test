# Part of Odoo. See LICENSE file for full copyright and licensing details.
#
# comu_accounting -- accounting engine for Odoo Community Edition.
#
# Bank reconciliation, deferred entries and financial reporting. Features are
# grouped into subpackages under models/, wizard/, views/, data/, security/
# and static/.

import logging

from odoo import Command

from . import demo
from . import models
from . import wizard
from . import controllers

_logger = logging.getLogger(__name__)


def _post_init_deferred_accounts(env):
    """Create the deferred-revenue and deferred-expense accounts.

    ISO 20022 and CAMT bank statement support live in the optional
    ``comu_accounting_payments`` addon. Installing them from here would force
    them on every user, so they are left to an explicit choice instead.
    """
    for company in env['res.company'].search([('chart_template', '!=', False)], order="parent_path"):
        ChartTemplate = env['account.chart.template'].with_company(company)
        ChartTemplate._load_data({
            'res.company': ChartTemplate._get_account_accountant_res_company(company.chart_template),
        })


def _post_init_tax_returns(env):
    """Generate the tax returns and set up their journal and deadlines."""
    env.ref('comu_accounting.ir_cron_generate_account_return')._trigger()

    companies = env['res.company'].search([])
    return_types = env['account.return.type'].search([])

    for company in companies:
        for return_type in return_types.with_company(company):
            return_type.deadline_periodicity = return_type.deadline_periodicity or return_type.default_deadline_periodicity
            return_type.deadline_start_date = return_type.deadline_start_date or return_type.default_deadline_start_date

    for company in env['res.company'].search([('chart_template', '!=', False)], order='parent_path'):
        ChartTemplate = env['account.chart.template'].with_company(company)
        # Set up the tax returns journal after the CoA was already installed.
        ChartTemplate._load_data({
            'account.journal': ChartTemplate._get_account_reports_journal(company.chart_template),
            'res.company': ChartTemplate._get_account_reports_res_company(company.chart_template),
        })


def _post_init_onboarding(env):
    """Run the accounting onboarding for each company with a chart of accounts.

    Cash-basis reporting lives in the optional ``comu_accounting_localization``
    addon, so it is not installed here; only the onboarding work is kept.
    """
    for company in env['res.company'].search([('chart_template', '!=', False)], order="parent_path"):
        company._initiate_account_onboardings()
        company.account_tax_return_journal_id.show_on_dashboard = True


def _comu_accounting_post_init(env):
    """Dispatcher for the three post-init steps.

    Order is significant: the deferred accounts must exist before the
    tax-return journal and company flags are added, and onboarding consumes
    that journal last.
    """
    _post_init_deferred_accounts(env)
    _post_init_tax_returns(env)
    _post_init_onboarding(env)


def uninstall_hook(env):
    """Restore the stock Odoo Community ``account`` group definitions.

    Leaves behind a clean Community install: group names and implied_ids are
    reverted and the accounting menus are re-parented under Invoicing.
    """
    # --- clear the basic group and unlink it from the manager --------------
    group_basic = env.ref('account.group_account_basic')
    group_manager = env.ref('account.group_account_manager')
    if group_basic:
        group_basic.write({'user_ids': [Command.clear()]})
        group_manager.write({'implied_ids': [Command.unlink(group_basic.id)]})

    # --- revert the groups this addon renamed ------------------------------
    try:
        group_user = env.ref("account.group_account_user")
        group_user.write({
            'name': "Show Full Accounting Features",
            'implied_ids': [(3, env.ref('account.group_account_invoice').id)],
        })
        group_readonly = env.ref("account.group_account_readonly")
        group_readonly.write({'name': "Show Full Accounting Features - Readonly"})
    except ValueError as e:
        _logger.warning(e)

    try:
        group_manager = env.ref("account.group_account_manager")
        group_manager.write({'name': "Billing Manager",
                             'implied_ids': [(4, env.ref("account.group_account_invoice").id),
                                             (3, env.ref("account.group_account_readonly").id),
                                             (3, env.ref("account.group_account_user").id)]})
    except ValueError as e:
        _logger.warning(e)

    # make the accounting features disappear (magic)
    env.ref("account.group_account_user").write({'user_ids': [(5, False, False)]})
    env.ref("account.group_account_readonly").write({'user_ids': [(5, False, False)]})

    # this menu should always be there, as the module depends on account.
    invoicing_menu = env.ref("account.menu_finance")
    for menu_xmlids in [
        "account.menu_finance_receivables",
        "account.menu_finance_payables",
        "account.menu_finance_entries",
        "account.menu_finance_reports",
        "account.menu_finance_configuration",
        "account.menu_board_journal_1",
    ]:
        try:
            env.ref(menu_xmlids).parent_id = invoicing_menu
        except ValueError as e:
            _logger.warning(e)