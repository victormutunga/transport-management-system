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
from openerp.tools.translate import _


# Fleet Vehicle odometer device


class FleetVehicleOdometerDevice(models.Model):
    _name = "fleet.vehicle.odometer.device"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "Fleet Vehicle Odometer Device"

    state = fields.Selection(
        [('draft', 'Draft'), ('active', 'Active'), ('inactive', 'Inactive'),
         ('cancel', 'Cancelled')], 'State', readonly=True, default='draft')
    date = fields.Datetime(
        string='Date', required=True,
        states={'cancel': [('readonly', True)],
                'active': [('readonly', True)],
                'inactive': [('readonly', True)]},
        default=(lambda *a: time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)))
    date_start = fields.Datetime(
        string='Date Start', required=True,
        states={'cancel': [('readonly', True)],
                'active': [('readonly', True)],
                'inactive': [('readonly', True)]},
        default=(lambda *a: time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)))
    date_end = fields.Datetime('Date End', readonly=True)
    name = fields.Char(
        string='Name', size=128, required=True,
        states={'cancel': [('readonly', True)],
                'active': [('readonly', True)],
                'inactive': [('readonly', True)]})
    vehicle_id = fields.Many2one(
        'fleet.vehicle', 'Vehicle', required=True, ondelete='cascade',
        states={'cancel': [('readonly', True)],
                'active': [('readonly', True)],
                'inactive': [('readonly', True)]})
    replacement_of = fields.Many2one(
        'fleet.vehicle.odometer.device', 'Replacement of',
        required=False, digits=(16, 2),
        states={'cancel': [('readonly', True)],
                'active': [('readonly', True)],
                'inactive': [('readonly', True)]})
    accumulated_start = fields.Float(
        string='Original Accumulated', help="Kms /Miles Accumulated from vehicle at \
        the moment of activation of this odometer", readonly=True)
    odometer_start = fields.Float(
        string='Start count', required=True,
        help="Initial counter from device",
        digits=(16, 2),
        states={'cancel': [('readonly', True)],
                'active': [('readonly', True)],
                'inactive': [('readonly', True)]},
        default=0.0)
    odometer_end = fields.Float(
        string='End count', required=True, help="Ending counter from device",
        digits=(16, 2),
        states={'cancel': [('readonly', True)],
                'active': [('readonly', True)],
                'inactive': [('readonly', True)]},
        default=0.0)
    odometer_reading_ids = fields.One2many(
        'fleet.vehicle.odometer', 'odometer_id',
        'Odometer Readings', readonly=True)

    def _check_state(self):
        # print "Entrando a _check_state "
        hubod_obj = self.pool.get('fleet.vehicle.odometer.device')
        for record in self.browse(self):
            # print "ID: ", record.id
            # print "State: ", record.state
            res = hubod_obj.search(
                [('vehicle_id', '=', record.vehicle_id.id),
                 ('state', 'not in', ('cancel', 'inactive')),
                 ('state', '=', record.state)], context=None)
            if res and res[0] and res[0] != record.id:
                return False
            return True

    def _check_odometer(self):
        # print "Entrando a _check_odometer"
        for rec in self.browse(self):
            # print "rec.odometer_end: ", rec.odometer_end
            # print "rec.odometer_start: ", rec.odometer_start
            if rec.odometer_end < rec.odometer_start:
                return False
            return True

    def _check_dates(self):
        # print "Entrando a _check_dates"
        hubod_obj = self.pool.get('fleet.vehicle.odometer.device')
        for record in self.browse(self):
            if record.date_end and record.date_end < record.date_start:
                raise Warning(
                    _('Error !'),
                    _('Ending Date (%s) is less than Starting \
                        Date (%s)') % (record.date_end, record.date_start))
            res = hubod_obj.search(
                [('vehicle_id', '=', record.vehicle_id.id),
                 ('state', '!=', 'cancel'),
                 ('date_end', '>', record.date_start)], context=None)
            # print "res: ", res
            if res and res[0] and res[0] != record.id:
                return False
            return True

    _constraints = [
        (_check_state, 'You can not have two records with the same \
            State (Draft / Active) !', ['state']),
        (_check_odometer, 'You can not have Odometer End less than \
            Odometer Start', ['odometer_end']),
        (_check_dates, 'You can not have this Star Date because is \
            overlaping with another record', ['date_end'])
    ]

    def write(self, vals):
        values = vals
        # print self._name, " vals: ", vals
        return super(FleetVehicleOdometerDevice, self).write(values)

    def on_change_vehicle_id(self, vehicle_id, date_start):
        odom_obj = self.pool.get('fleet.vehicle.odometer.device')
        res = odom_obj.search(
            [('vehicle_id', '=', vehicle_id),
             ('state', '!=', 'cancel'),
             ('date_end', '<', date_start)],
            limit=1, order="date_end desc", context=None)
        odometer_id = False
        accumulated = 0.0
        # print "res: ", res
        if res and res[0]:
            for rec in odom_obj.browse(res):
                odometer_id = rec.id
                accumulated = rec.vehicle_id.odometer
        return {'value':
                {'replacement_of': odometer_id, 'accumulated': accumulated}}

    def action_activate(self):
        for rec in self.browse(self):
            odometer = rec.vehicle_id.odometer
            self.write(
                {'state': 'active', 'accumulated': odometer})
        return True

    def action_inactivate(self):
        for rec in self.browse(self):
            self.write(
                {'state': 'inactive',
                 'date_end': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)})
        return True

    def action_cancel(self):
        for rec in self.browse(self):
            self.write({'state': 'cancel'})
        return True
