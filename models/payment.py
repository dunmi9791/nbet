from odoo import fields, models, api



class AccountAsset(models.Model):
    _inherit = 'account.payment'

    voucher_payment_id = fields.Many2one(
        comodel_name='payment_voucher.ebs',
        string='Voucher_payment_id',
        required=False)