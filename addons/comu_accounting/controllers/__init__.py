# Part of Odoo. See LICENSE file for full copyright and licensing details.
# controllers packages of comu_accounting.
#
# Load order is load-bearing: Odoo resolves _inherit at class
# definition time, so a module extending another's model must be
# imported after it.

from . import account_reports
