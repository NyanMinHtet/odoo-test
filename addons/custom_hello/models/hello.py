from odoo import models, fields

class CustomHello(models.Model):
    _name = 'custom.hello'
    _description = 'Custom Hello Record'

    name = fields.Char(string='Name', required=True)
    message = fields.Text(string='Message')
