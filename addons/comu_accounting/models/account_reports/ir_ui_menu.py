from odoo import models


class IrUiMenu(models.Model):
    _inherit = 'ir.ui.menu'

    def _get_account_readonly_menu_ids(self):
        res = super()._get_account_readonly_menu_ids()
        res.extend([
            'comu_accounting.menu_action_account_report_multicurrency_revaluation',
            'comu_accounting.menu_action_account_report_tree',
        ])
        return res
