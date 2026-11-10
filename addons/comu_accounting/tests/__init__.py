# Part of Odoo. See LICENSE file for full copyright and licensing details.
#
# Odoo discovers test modules by scanning this package for submodules whose
# name starts with 'test_', so the per-source-module suites are flattened
# here. Shared helpers keep a common_<module>_ prefix instead of plain
# 'common' because two sources each ship a common.py.

from . import test_account_auto_reconcile_wizard
from . import test_account_bank_statement
from . import test_account_bank_statement_tour
from . import test_account_fiscal_year
from . import test_account_payment
from . import test_account_reconcile_wizard
from . import test_account_reports_annotations_export
from . import test_account_reports_filters
from . import test_account_reports_journal_filter
from . import test_account_reports_tours
from . import test_account_returns
from . import test_account_sales_report_generic
from . import test_aged_payable_report
from . import test_aged_receivable_report
from . import test_all_reports_generation
from . import test_analytic_reports
from . import test_balance_sheet_balanced
from . import test_balance_sheet_report
from . import test_budget
from . import test_cash_flow_report
from . import test_change_lock_date_wizard
from . import test_currency_table
from . import test_deferred_management
from . import test_deferred_reports
from . import test_financial_report
from . import test_followup_report
from . import test_general_ledger_report
from . import test_journal_report
from . import test_kpi_provider
from . import test_multicurrencies_revaluation_report
from . import test_partner_ledger_report
from . import test_prediction
from . import test_reconciliation_matching_rules
from . import test_reconciliation_report
from . import test_report_engines
from . import test_report_sections
from . import test_signature
from . import test_tax_report
from . import test_tax_report_carryover
from . import test_tax_report_default_part
from . import test_tour
from . import test_tour_account_reports
from . import test_tour_analytic_filters
from . import test_trial_balance_report
from . import test_ui
