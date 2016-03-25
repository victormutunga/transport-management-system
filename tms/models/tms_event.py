# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time

from openerp import fields, models
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT


class TmsEvent(models.Model):
    _name = "tms.event"
    _description = "Events"

    state = fields.Selection(
        [('draft', 'Draft'), ('confirmed', 'Confirmed'),
         ('cancel', 'Cancelled')], 'State', readonly=True)
    name = fields.Char(
        'Description', size=250, required=True, readonly=False,
        states={'confirmed': [('readonly', True)],
                'cancel': [('readonly', True)]})
    date = fields.Datetime(
        'Date', required=True, readonly=False,
        states={'confirmed': [('readonly', True)],
                'cancel': [('readonly', True)]})
    category_id = fields.Many2one(
        'tms.event.category', 'Category', select=True, required=True,
        readonly=False,
        states={'confirmed': [('readonly', True)],
                'cancel': [('readonly', True)]}, ondelete='restrict')
    action_ids = fields.Many2many(
        compute='category_id.action_ids',
        relation='tms.event.action', string='Actions', readonly=True)
    notes = fields.Text(
        'Notes', readonly=False, states={'confirmed': [('readonly', True)],
                                         'cancel': [('readonly', True)]})
    travel_id = fields.Many2one(
        'tms.travel', 'Travel', select=True, required=True, readonly=False,
        states={'confirmed': [('readonly', True)],
                'cancel': [('readonly', True)]}, ondelete='restrict')
    unit_id = fields.Many2one(
        compute='travel_id.unit_id', relation='fleet.vehicle',
        string='Unit', store=True, readonly=True)
    trailer1_id = fields.Many2one(
        compute='travel_id.trailer1_id', relation='fleet.vehicle',
        string='Trailer 1', store=True, readonly=True)
    dolly_id = fields.Many2one(
        compute='travel_id.dolly_id', relation='fleet.vehicle',
        string='Dolly', store=True, readonly=True)
    trailer2_id = fields.Many2one(
        compute='travel_id.trailer2_id', relation='fleet.vehicle',
        string='Trailer 2', store=True, readonly=True)
    employee_id = fields.Many2one(
        compute='travel_id.employee_id', relation='hr.employee',
        string='Driver', store=True, readonly=True)
    route_id = fields.Many2one(
        compute='travel_id.route_id', relation='tms.route',
        string='Route', store=True, readonly=True)
    departure_id = fields.Many2one(
        compute='route_id.departure_id', relation='tms.place',
        string='Departure', store=True, readonly=True)
    arrival_id = fields.Many2one(
        compute='route_id.arrival_id', relation='tms.place',
        string='Arrival', store=True, readonly=True)
    waybill_id = fields.Many2one(
        'tms.waybill', 'Waybill', readonly=False,
        states={'confirmed': [('readonly', True)],
                'cancel': [('readonly', True)]}, ondelete='restrict')
    latitude = fields.Float(
        'Latitude', readonly=False,
        states={'confirmed': [('readonly', True)],
                'cancel': [('readonly', True)]})
    longitude = fields.Float(
        'Longitude', readonly=False,
        states={'confirmed': [('readonly', True)],
                'cancel': [('readonly', True)]})
    origin = fields.Char(
        'Origin', size=64, required=True, readonly=False,
        states={'confirmed': [('readonly', True)],
                'cancel': [('readonly', True)]})
    position_real = fields.Text(
        'Position Real', help="Position as GPS", readonly=False,
        states={'confirmed': [('readonly', True)],
                'cancel': [('readonly', True)]})
    position_pi = fields.Text(
        'Position P.I.', help="Position near a Point of Interest",
        readonly=False, states={'confirmed': [('readonly', True)],
                                'cancel': [('readonly', True)]})
    message = fields.Text(
        'Message', readonly=False,
        states={'confirmed': [('readonly', True)],
                'cancel': [('readonly', True)]})
    shop_id = fields.Many2one(
        compute='travel_id.shop_id', relation='sale.shop',
        string='Shop', store=True, readonly=True)
    company_id = fields.Many2one(
        compute='shop_id.company_id', relation='res.company',
        string='Company', store=True, readonly=True)

    _defaults = {
        'date': lambda *a: time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
        'origin': 'TMS',
        'state': lambda *a: 'draft',
    }

    _order = "date, category_id"

    def action_cancel(self, cr, uid, ids, *args):
        if not len(ids):
            return False
        for rec in self.browse(cr, uid, ids):
            self.write(cr, uid, ids, {'state': 'cancel'})
        return True

    def action_draft(self, cr, uid, ids, *args):
        if not len(ids):
            return False
        for rec in self.browse(cr, uid, ids):
            self.write(cr, uid, ids, {'state': 'draft'})
        return True

    def action_confirm(self, cr, uid, ids, *args):
        if not len(ids):
            return False
        # Execute actions related to Event Category
        for rec in self.browse(cr, uid, ids):
            for action in rec.action_ids:
                exec action.get_value
            self.write(cr, uid, ids, {'state': 'confirmed'})
        return True
