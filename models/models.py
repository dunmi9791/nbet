# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime
from datetime import date
from odoo.exceptions import UserError
from odoo.tools.translate import _




class PaymentVoucher(models.Model):
    _name = 'payment_voucher.ebs'
    _rec_name = 'voucher_no'
    _description = 'payment voucher'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char()
    voucher_type = fields.Many2one(comodel_name="voucher_type.ebs", string='Voucher Type')
    address = fields.Text(string="Address", required=False, )
    class_code = fields.Char(string="Classification Code", required=False, )
    voucher_no = fields.Char(string="Voucher Number", default=lambda self: _('New'), requires=False, readonly=True,
                             trace_visibility='onchange', )
    voucher_details_ids = fields.One2many(comodel_name="voucher_details.ebs", inverse_name="voucher_id",
                                          string="Voucher Details", required=False, )
    payable_at = fields.Char(string="Payable At", required=False, )
    originating_memo = fields.Char(string="Originating Memo", required=False, readonly=True)
    state = fields.Selection(string="",
                             selection=[('draft', 'draft'), ('Prepared', 'Prepared'), ('FC Sign Off', 'FC Sign Off'),
                                        ('CFO Approval', 'CFO Approval'),
                                        ('process', 'Processed'),
                                        ('Rejected', 'Rejected'), ], required=False, copy=False, default='draft',
                             readonly=True, track_visibility='onchange', )
    amount = fields.Float('Amount', compute='_amount', store=True)
    account_id = fields.Many2one(string="Debit Account", comodel_name='account.account')
    inv_obj = fields.Many2one('account.invoice', invisible=1)
    budget_position_id = fields.Many2one(comodel_name="account.budget.post", string="Budgetary Position", required=False, )
    # budget_position = fields.Integer(string="Budgetary Position", compute='_total_realised', store=True)
    analytic_id_id = fields.Many2one(comodel_name="account.analytic.account", string="Budget Line", required=False, )
    mode_payment = fields.Many2one(comodel_name='account.journal', string='Payment Mode')
    narration = fields.Text(
        string="Narration",
        required=False)
    active = fields.Boolean(
        string='Active', 
        required=False, default=True)
    date = fields.Date(string="Date", required=False, )

    # @api.one
    # @api.depends('analytic_id_id', )
    # def _total_realised(self):
    #
    #     self.total_realised = sum(paid.installment
    #                               for paid in self.schedule_installments_ids.filtered(lambda o: o.state == 'paid'))

    @api.model
    def create(self, vals):
        if vals.get('voucher_no', _('New')) == _('New'):
            vals['voucher_no'] = self.env['ir.sequence'].next_by_code('increment_payment_voucher') or _('New')
        result = super(PaymentVoucher, self).create(vals)
        return result

    @api.one
    @api.depends('voucher_details_ids.rate', )
    def _amount(self):
        self.amount = sum(voucher_details.rate for voucher_details in self.voucher_details_ids)

    # @api.multi
    # def open_vouchers(self):
    #     total_len = self.env['payment_voucher.ebs'].search_count([])
    #     result = total_len
    #     return result
    #



    @api.multi
    def is_allowed_transition(self, old_state, new_state):
        allowed = [('draft', 'Prepared'),
                   ('Prepared', 'FC Sign Off'),
                   ('FC Sign Off', 'Rejected'),
                   ('FC Sign Off', 'CFO Approval'),
                   ('CFO Approval', 'process'),
                   ('process', 'CFO Approval'),
                   ]
        return (old_state, new_state) in allowed

    @api.multi
    def change_state(self, new_state):
        for voucher in self:
            if voucher.is_allowed_transition(voucher.state, new_state):
                voucher.state = new_state
            else:
                msg = _('Moving from %s to %s is not allowed') % (voucher.state, new_state)
                raise UserError(msg)

    @api.multi
    def payment_voucher_request(self):
        self.change_state('Prepared')

    @api.multi
    def payment_voucher_prepare(self):
        self.change_state('FC Sign Off')

    @api.multi
    def voucher_cfo_approve(self):
        self.change_state('CFO Approval')

    @api.multi
    def payment_voucher_process(self):
        if not self.voucher_type:
            raise UserError(_('You Have to enter Voucher type to post Voucher'))
        if not self.voucher_details_ids.payee_id:
            raise UserError(_('You Have to enter payee to post Voucher'))

        inv_line_obj = self.env['account.invoice']
        for bill_val in self.voucher_details_ids:
            bill_vals = []
            bill_details = {
                'type': 'in_invoice',
                'partner_id': bill_val.payee_id.id,
                'reference': self.voucher_no,
                'origin': self.originating_memo,
                'invoice_line_ids': [(0, 0, {
                                             'name': bill_val.details,
                                             'account_id': self.voucher_type.account_id.id,
                                             'quantity': 1,
                                             'price_unit': bill_val.rate, })]
            }
            bill_vals.append(bill_details)
            inv_line_obj.create(bill_vals)


        self.change_state('process')


class VoucherDetails(models.Model):
    _name = 'voucher_details.ebs'
    _rec_name = 'name'
    _description = 'New Description'

    name = fields.Char()
    voucher_id = fields.Many2one(comodel_name="payment_voucher.ebs", string="", required=False, )
    details = fields.Text(string="Particulars", required=False, )
    payee_id = fields.Many2one('res.partner', string='Payee', track_visibility='onchange', )
    rate = fields.Float(string="Rate/Amount",  required=False, )
    payee_type = fields.Selection(
        string='Payee Type',
        selection=[('vendor', 'Vendor'),
                   ('disco', 'Disco'),
                   ('genco', 'Genco'),
                   ('employee', 'Employee'), ],
        required=False, )


class PaymentMandate(models.Model):
    _name = 'payment_mandate.ebs'
    _rec_name = 'mandate_no'
    _description = 'Payment Mandate'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char()
    payee_id = fields.Many2one('res.partner', string='Payee', track_visibility='onchange', readonly=True,
                               states={'draft': [('readonly', False)], 'Fin Approve': [('readonly', False)]}, )
    description = fields.Text(string="Description", required=False, )
    date = fields.Date(string="Date", required=False, )
    mandate_ref = fields.Char(string="Mandate Reference")
    amount = fields.Float(string="Amount")
    mode = fields.Selection(string="Mode of settlement", selection=[('Remita', 'Remita'), ('GIFMIS', 'GIFMIS'), ],
                            required=False, )
    account_no = fields.Char(string="Account Number")
    bank = fields.Char(string="Bank")
    account_name = fields.Char(string="Account Name")
    state = fields.Selection(string="",
                             selection=[('draft', 'draft'), ('Forward', 'Forward'), ('FC Review', 'FC Review'),
                                        ('CFO Review', 'CFO Review'), ('CEO Approval', 'CEO Approval'),
                                        ('Audit Review', 'Audit Review'), ('CFO forward', 'CFO forward'), ('FC forward', 'FC forward'),
                                        ('Dispatch', 'Dispatch'), ('acknowledge', 'acknowledge'),
                                        ('Rejected', 'Rejected'), ], required=False, copy=False, default='draft',
                             readonly=True, track_visibility='onchange', )
    mandate_no = fields.Char(string="Mandate Number", default=lambda self: _('New'), requires=False, readonly=True,
                             trace_visibility='onchange', )

    @api.model
    def create(self, vals):
        if vals.get('mandate_no', _('New')) == _('New'):
            vals['mandate_no'] = self.env['ir.sequence'].next_by_code('increment_payment_mandate') or _('New')
        result = super(PaymentMandate, self).create(vals)
        return result



class DiscoInvoicing(models.Model):
    _name = 'disco_invoicing.ebs'
    _description = 'DiscoInvoicing'

    name = fields.Char(string='Billing Circle', compute="billing_circle")
    month = fields.Selection(selection=[('JAN', 'January'), ('FEB', 'February'), ('MAR', 'March'), ('APR', 'April'),
                              ('MAY', 'May'), ('JUN', 'June'), ('JUL', 'July'), ('AUG', 'August'),
                              ('AUG', 'September'), ('OCT', 'October'), ('NOV', 'November'), ('DEC', 'December'), ],
                             string='Billing Month',)
    year = fields.Selection(selection='_get_years', string='Billing Year', store=True)
    disco = fields.Many2one(comodel_name='res.partner', string='Disco', required=False)
    invoice_date = fields.Date(string='Date of Invoicing', required=False)
    submission_date = fields.Date(string='Invoice Submission Date', required=False)
    minimum_remitance = fields.Float(string='Minimum Remittance Amount', )
    invoice_due_date = fields.Date(string='Invoice Due Date')
    invoice_id = fields.Many2one(string='Invoice', comodel_name='account.invoice', )
    disco_outstanding = fields.Float(string='Total Outstanding')
    outstanding_no_interest = fields.Float(string='Outstanding less interest',)
    interest_period = fields.Float(string='Interest outstanding for the period',)
    cummulative_interest = fields.Float(string='Total Interest')


    @api.multi
    @api.depends('')
    def _get_years(self):
        year_list = []
        for i in range(2010, 2036):
            year_list.append((i, str(i)))
        return year_list


    @api.one
    @api.depends('month', 'year')
    def billing_circle(self):
        for record in self:
            m = record.month
            y = record.year
            record['name'] = ("%s%s" % (m ,y))


class VoucherType(models.Model):
    _name = 'voucher_type.ebs'
    _description = 'VoucherType'

    name = fields.Char()
    account_id = fields.Many2one(comodel_name='account.account', string='Account')
    analytic_account_id = fields.Many2one(comodel_name='account.analytic.account', string='Budget Line/Analytic Account')
    mode_payment = fields.Many2one(comodel_name='account.journal', string='Payment Account')
    bill_journal = fields.Many2one(comodel_name='account.journal', string='Expense Journal')


class VoucherPayment(models.Model):
    _name = 'voucher_payment.ebs'
    _rec_name = 'name'
    _description = 'payment voucher'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char()
    voucher_type = fields.Many2one(comodel_name="voucher_type.ebs", string='Voucher Type')
    mode_payment = fields.Many2one(comodel_name='account.journal', string='Payment Mode')
    payee_id = fields.Many2one('res.partner', string='Payee', track_visibility='onchange', readonly=True,
                               states={'draft': [('readonly', False)], 'Fin Approve': [('readonly', False)]}, )
    cost_centre = fields.Selection(
        string='Cost Centre',
        selection=[('vendor', 'Vendor'),
                   ('disco', 'Disco'),
                   ('genco', 'Genco'),
                   ('employee', 'Employee'),],
        required=False, )
    invoice_id = fields.Many2one(string='Invoice', comodel_name='account.invoice', )
    rate = fields.Float(string="Amount", required=False, )

# class nbet__process(models.Model):
#     _name = 'nbet__process.nbet__process'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100
