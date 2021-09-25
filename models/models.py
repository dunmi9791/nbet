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
