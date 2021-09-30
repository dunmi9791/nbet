# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime
from datetime import date
from odoo.exceptions import UserError
from odoo.tools.translate import _


class TravelAdvanceRequest(models.Model):
    _name = 'travel_advance.nbet_process'
    _rec_name = 'request_no'
    _description = 'Table for handling travel request '
    _inherit = ['mail.thread', 'mail.activity.mixin']

    request_no = fields.Char(string="Request Number", default=lambda self: _('New'), requires=False, readonly=True,
                             trace_visibility='onchange', )
    request_date = fields.Datetime(string="Date/Time of request", required=False, )
    traveller_name = fields.Char(string="Name of Traveller", required=False, )
    travel_date = fields.Date(string="Date of Travel", required=False, )
    destination = fields.Char(string="Organisation/Destination", required=False,)
    traveller_address = fields.Text(string="Traveller Address", required=False, )
    grade_level = fields.Selection(string="Grade Level", selection=[('Grade Level 1', 'Grade Level 1'), ('Grade Level 2', 'Grade Level 2'), ], required=False, )
    travel_details_ids = fields.One2many(comodel_name="travel.details", inverse_name="travel_request_id",
                                         string="Travel Details", required=False, )
    amount_total = fields.Float('Total', compute='_amount_total', store=True)
    justification = fields.Text(string="Justification", required=False, )
    state = fields.Selection(string="",
                             selection=[('draft', 'draft'), ('Requested', 'Requested'), ('HOD Approve', 'HOD Approval'),
                                        ('Fin Approve', 'Fin Approved'),  ('process', 'Processed'),
                                        ('Rejected', 'Rejected'), ], required=False, copy=False, default='draft',
                             readonly=True, track_visibility='onchange', )

    @api.model
    def create(self, vals):
        if vals.get('request_no', _('New')) == _('New'):
            vals['request_no'] = self.env['ir.sequence'].next_by_code('increment_travel_request') or _('New')
        result = super(TravelAdvanceRequest, self).create(vals)
        return result

    @api.one
    @api.depends('travel_details_ids.total', )
    def _amount_total(self):
        self.amount_total = sum(travel_details.total for travel_details in self.travel_details_ids)

    @api.multi
    def is_allowed_transition(self, old_state, new_state):
        allowed = [('draft', 'Requested'),
                   ('Requested', 'HOD Approve'),
                   ('Requested', 'Rejected'),
                   ('HOD Approve', 'Fin Approve'),
                   ('Fin Approve', 'process'),
                   ('HOD Approve', 'Rejected'),
                   ]
        return (old_state, new_state) in allowed

    @api.multi
    def change_state(self, new_state):
        for travel in self:
            if travel.is_allowed_transition(travel.state, new_state):
                travel.state = new_state
            else:
                msg = _('Moving from %s to %s is not allowed') % (travel.state, new_state)
                raise UserError(msg)

    @api.multi
    def travel_advance_request(self):
        self.change_state('Requested')

    @api.multi
    def travel_advance_approve(self):
        self.change_state('HOD Approve')

    @api.multi
    def travel_advance_fin_approve(self):
        self.change_state('Fin Approve')

    @api.multi
    def travel_advance_reject(self):
        self.change_state('Rejected')

    @api.multi
    def travel2_advance_reject(self):
        self.change_state('Rejected')

    @api.multi
    def process(self):
        self.change_state('process')


class TravelDetails(models.Model):
    _name = 'travel.details'
    _rec_name = 'name'
    _description = 'Hold details of travel request'

    name = fields.Char()
    travel_request_id = fields.Many2one(comodel_name="travel_advance.nbet_process", string="", required=False, )
    location = fields.Char(string="Location", required=False, )
    allowance = fields.Char(string="Allowance", required=False, )
    rates = fields.Float(string="Rates",  required=False, )
    days = fields.Integer(string="Days", required=False, )
    total = fields.Float(string="Total",  required=False, compute='_compute_price_subtotal', store=True, digits=0 )

    @api.one
    @api.depends('rates', 'days',  )
    def _compute_price_subtotal(self):
        self.total = self.rates * self.days


class AdvanceRequest(models.Model):
    _name = 'advance_request.ebs'
    _rec_name = 'request_no'
    _description = 'Table for Advance request'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Names")
    request_no = fields.Char(string="Request Number", default=lambda self: _('New'), requires=False, readonly=True,
                             trace_visibility='onchange', )
    designation = fields.Char(string="Designation", required=False, )
    purpose = fields.Char(string="Purpose of Advance", required=False, )
    date = fields.Date(string="Date of Advance", required=False, )
    advance_details_ids = fields.One2many(comodel_name="advance_details.ebs", inverse_name="advance_request_id",
                                         string="Advance Details", required=False, )
    amount_total = fields.Float('Total Amount', compute='_amount_total', store=True)
    state = fields.Selection(string="",
                             selection=[('draft', 'draft'), ('Requested', 'Requested'), ('HOD Approve', 'HOD Approval'),
                                        ('FC Approve', 'FC Approved'), ('CFO Approve', 'CFO Approved'),
                                        ('CEO Approve', 'CEO Approved'), ('CFO Forward', 'CFO Forward'),
                                        ('Input Details', 'Input Details'), ('Review Details', 'Review Details'),
                                        ('process', 'Processed'),
                                        ('Rejected', 'Rejected'), ], required=False, copy=False, default='draft',
                             readonly=True, track_visibility='onchange', )

    @api.one
    @api.depends('advance_details_ids.amount', )
    def _amount_total(self):
        self.amount_total = sum(advance_details.amount for advance_details in self.advance_details_ids)

    @api.model
    def create(self, vals):
        if vals.get('request_no', _('New')) == _('New'):
            vals['request_no'] = self.env['ir.sequence'].next_by_code('increment_staff_advance') or _('New')
        result = super(AdvanceRequest, self).create(vals)
        return result

    @api.multi
    def is_allowed_transition(self, old_state, new_state):
        allowed = [('draft', 'Requested'),
                   ('Requested', 'HOD Approve'),
                   ('Requested', 'Rejected'),
                   ('HOD Approve', 'FC Approve'),
                   ('FC Approve', 'CFO Approve'),
                   ('HOD Approve', 'Rejected'),
                   ('CFO Approve', 'CEO Approve'),
                   ('CEO Approve', 'CFO Forward'),
                   ('CFO Forward', 'Input Details'),
                   ('Input Details', 'Review Details'),
                   ('Review Details', 'Processed'),
                   ('FC Approved', 'Rejected'),
                   ('CFO Approved', 'Rejected'),
                   ]
        return (old_state, new_state) in allowed

    @api.multi
    def change_state(self, new_state):
        for advance in self:
            if advance.is_allowed_transition(advance.state, new_state):
                advance.state = new_state
            else:
                msg = _('Moving from %s to %s is not allowed') % (advance.state, new_state)
                raise UserError(msg)

    @api.multi
    def staff_advance_request(self):
        self.change_state('Requested')

    @api.multi
    def staff_advance_hod_approve(self):
        self.change_state('HOD Approve')

    @api.multi
    def staff_advance_fc_approve(self):
        self.change_state('FC Approve')

    @api.multi
    def staff_advance_ceo_approve(self):
        self.change_state('CEO Approve')

    @api.multi
    def staff_advance_cfo_approve(self):
        self.change_state('CFO Approve')

    @api.multi
    def staff_advance_input_details(self):
        self.change_state('Input Details')

    @api.multi
    def staff_advance_review_details(self):
        self.change_state('Review Details')

    @api.multi
    def staff_advance_cfo_forward(self):
        self.change_state('CFO Forward')

    @api.multi
    def staff2_advance_reject(self):
        self.change_state('Rejected')

    @api.multi
    def process(self):
        self.change_state('process')


class AdvanceDetails(models.Model):
    _name = 'advance_details.ebs'
    _rec_name = 'name'
    _description = 'Table for details of advance'

    name = fields.Char()
    description = fields.Char(string="Description", required=False, )
    amount = fields.Float(string="Amount",  required=False, )
    advance_request_id = fields.Many2one(comodel_name="advance_request.ebs", string="", required=False, )


class PaymentVoucher(models.Model):
    _name = 'payment_voucher.ebs'
    _rec_name = 'voucher_no'
    _description = 'payment voucher'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char()
    deptal_no = fields.Char(string="Deptal Number", required=False, )
    payee = fields.Char(string="Payee", required=False, )
    address = fields.Text(string="Address", required=False, )
    class_code = fields.Char(string="Classification Code", required=False, )
    voucher_no = fields.Char(string="Voucher Number", default=lambda self: _('New'), requires=False, readonly=True,
                             trace_visibility='onchange', )
    voucher_details_ids = fields.One2many(comodel_name="voucher_details.ebs", inverse_name="voucher_id",
                                          string="Voucher Details", required=False, )
    payable_at = fields.Char(string="Payable At", required=False, )
    originating_memo = fields.Char(string="Originating Memo", required=False, )
    state = fields.Selection(string="",
                             selection=[('draft', 'draft'), ('Prepared', 'Prepared'), ('FC Sign Off', 'FC Sign Off'),
                                        ('CFO Approval', 'CFO Approval'),
                                        ('process', 'Processed'),
                                        ('Rejected', 'Rejected'), ], required=False, copy=False, default='draft',
                             readonly=True, track_visibility='onchange', )

    @api.model
    def create(self, vals):
        if vals.get('voucher_no', _('New')) == _('New'):
            vals['voucher_no'] = self.env['ir.sequence'].next_by_code('increment_payment_voucher') or _('New')
        result = super(PaymentVoucher, self).create(vals)
        return result

    @api.multi
    def is_allowed_transition(self, old_state, new_state):
        allowed = [('draft', 'Prepared'),
                   ('Prepared', 'FC Sign Off'),
                   ('FC Sign Off', 'Rejected'),
                   ('FC Sign Off', 'CFO Approval'),
                   ('process', 'CFO Approve'),
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


class VoucherDetails(models.Model):
    _name = 'voucher_details.ebs'
    _rec_name = 'name'
    _description = 'New Description'

    name = fields.Char()
    voucher_id = fields.Many2one(comodel_name="payment_voucher.ebs", string="", required=False, )
    date = fields.Date(string="Date", required=False, )
    details = fields.Text(string="Detailed Description of Service and Work", required=False, )
    rate = fields.Float(string="Rate/Amount",  required=False, )










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
