# -*- coding: utf-8 -*-
# © <2012> <Israel Cruz Argil, Argil Consulting>
# © <2016> <Jarsa Sistemas, S.A. de C.V.>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


class TmsEvent(models.Model):
    _name = "tms.event"
    _description = "Events"
    _order = "date"

    name = fields.Char(
        string='Description', required=True)
    state = fields.Selection(
        [('draft', 'Draft'), ('confirmed', 'Confirmed'),
         ('cancel', 'Cancelled')], 'State', readonly=True)
    date = fields.Date(
        default=fields.Date.today,
        string='Date', required=True,
        states={'confirmed': [('readonly', True)],
                'cancel': [('readonly', True)]})
    notes = fields.Text(
        string='Notes', states={'confirmed': [('readonly', True)],
                                'cancel': [('readonly', True)]})
    travel_id = fields.Many2one(
        'tms.travel', 'Travel', select=True, required=True, readonly=False,
        states={'confirmed': [('readonly', True)],
                'cancel': [('readonly', True)]}, ondelete='restrict')
    latitude = fields.Float(
        string='Latitude',
        states={'confirmed': [('readonly', True)],
                'cancel': [('readonly', True)]})
    longitude = fields.Float(
        string='Longitude',
        states={'confirmed': [('readonly', True)],
                'cancel': [('readonly', True)]})
    origin = fields.Char(
        string='Origin', size=64, required=True,
        states={'confirmed': [('readonly', True)],
                'cancel': [('readonly', True)]})
    position_real = fields.Text(
        string='Position Real', help="Position as GPS",
        states={'confirmed': [('readonly', True)],
                'cancel': [('readonly', True)]})
    position_pi = fields.Text(
        string='Position P.I.', help="Position near a Point of Interest",
        states={'confirmed': [('readonly', True)],
                'cancel': [('readonly', True)]})
    message = fields.Text(
        string='Message',
        states={'confirmed': [('readonly', True)],
                'cancel': [('readonly', True)]})
