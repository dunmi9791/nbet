# -*- coding: utf-8 -*-

from odoo import models, fields, api


class TravelAdvanceRequest(models.Model):
    _name = 'travel_advance.nbet_process'
    _rec_name = 'name'
    _description = 'Table for handling travel request '

    name = fields.Char()
    request_date = fields.Datetime(string="Date/Time of request", required=False, )
    traveller_name = fields.Char(string="Name of Traveller", required=False, )
    travel_date = fields.Date(string="Date of Travel", required=False, )
    destination = fields.Char(string="Organisation/Destination", required=False,)
    traveller_address = fields.Text(string="Traveller Address", required=False, )
    grade_level = fields.Selection(string="Grade Level", selection=[('Grade Level 1', 'Grade Level 1'), ('Grade Level 2', 'Grade Level 2'), ], required=False, )
    travel_details_ids = fields.One2many(comodel_name="travel.details", inverse_name="travel_request_id",
                                         string="Travel Details", required=False, )
    justification = fields.Text(string="Justification", required=False, )


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
    total = fields.Float(string="Total",  required=False, )



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
