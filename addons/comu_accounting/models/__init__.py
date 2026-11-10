# Part of Odoo. See LICENSE file for full copyright and licensing details.
# models packages of comu_accounting.
#
# Load order is load-bearing: Odoo resolves _inherit at class
# definition time, so a module extending another's model must be
# imported after it.

# account_accountant -> account_reports -> accountant

from . import account_accountant
from . import account_reports
from . import accountant
