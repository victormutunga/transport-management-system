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
from openerp.osv import osv, fields
import time
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT


class tms_event(osv.osv):
    _name = "tms.event"
    _description = "Events"

    _columns = {
        'state': fields.selection([('draft', 'Draft'), ('confirmed', 'Confirmed'), ('cancel', 'Cancelled')], 'State', readonly=True),
        'name': fields.char('Description', size=250, required=True, readonly=False, states={'confirmed': [('readonly', True)], 'cancel': [('readonly', True)]}),
        'date': fields.datetime('Date', required=True, readonly=False, states={'confirmed': [('readonly', True)], 'cancel': [('readonly', True)]}),
        'category_id': fields.many2one('tms.event.category', 'Category', select=True, required=True, readonly=False, states={'confirmed': [('readonly', True)], 'cancel': [('readonly', True)]}, ondelete='restrict'),
        'action_ids': fields.related('category_id', 'action_ids', type='many2many', relation='tms.event.action', string='Actions', readonly=True),
        'notes': fields.text('Notes', readonly=False, states={'confirmed': [('readonly', True)], 'cancel': [('readonly', True)]}),
        'travel_id': fields.many2one('tms.travel', 'Travel', select=True, required=True, readonly=False, states={'confirmed': [('readonly', True)], 'cancel': [('readonly', True)]}, ondelete='restrict'),
        'unit_id': fields.related('travel_id', 'unit_id', type='many2one', relation='fleet.vehicle', string='Unit', store=True, readonly=True),
        'trailer1_id': fields.related('travel_id', 'trailer1_id', type='many2one', relation='fleet.vehicle', string='Trailer 1', store=True, readonly=True),
        'dolly_id': fields.related('travel_id', 'dolly_id', type='many2one', relation='fleet.vehicle', string='Dolly', store=True, readonly=True),
        'trailer2_id': fields.related('travel_id', 'trailer2_id', type='many2one', relation='fleet.vehicle', string='Trailer 2', store=True, readonly=True),
        'employee_id': fields.related('travel_id', 'employee_id', type='many2one', relation='hr.employee', string='Driver', store=True, readonly=True),
        'route_id': fields.related('travel_id', 'route_id', type='many2one', relation='tms.route', string='Route', store=True, readonly=True),
        'departure_id': fields.related('route_id', 'departure_id', type='many2one', relation='tms.place', string='Departure', store=True, readonly=True),
        'arrival_id': fields.related('route_id', 'arrival_id', type='many2one', relation='tms.place', string='Arrival', store=True, readonly=True),
        'waybill_id': fields.many2one('tms.waybill', 'Waybill', readonly=False, states={'confirmed': [('readonly', True)], 'cancel': [('readonly', True)]}, ondelete='restrict'),
        'latitude': fields.float('Latitude', readonly=False, states={'confirmed': [('readonly', True)], 'cancel': [('readonly', True)]}),
        'longitude': fields.float('Longitude', readonly=False, states={'confirmed': [('readonly', True)], 'cancel': [('readonly', True)]}),
        'origin': fields.char('Origin', size=64, required=True, readonly=False, states={'confirmed': [('readonly', True)], 'cancel': [('readonly', True)]}),
        'position_real': fields.text('Position Real', help="Position as GPS", readonly=False, states={'confirmed': [('readonly', True)], 'cancel': [('readonly', True)]}),
        'position_pi': fields.text('Position P.I.', help="Position near a Point of Interest", readonly=False, states={'confirmed': [('readonly', True)], 'cancel': [('readonly', True)]}),
        'message': fields.text('Message', readonly=False, states={'confirmed': [('readonly', True)], 'cancel': [('readonly', True)]}),
        'shop_id': fields.related('travel_id', 'shop_id', type='many2one', relation='sale.shop', string='Shop', store=True, readonly=True),
        'company_id': fields.related('shop_id', 'company_id', type='many2one', relation='res.company', string='Company', store=True, readonly=True),
    }

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
