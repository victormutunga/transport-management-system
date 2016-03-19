
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


from openerp import models, fields
from openerp.tools.translate import _

# Vehicle Odometer records


class FleetVehicleOdometer(models.Model):
    _inherit = ['fleet.vehicle.odometer']
    _name = 'fleet.vehicle.odometer'
#  PENDIENTES
# - CALCULAR LA DISTANCIA RECORRIDA ENTRE EL REGISTRO ACTUAL Y EL ANTERIOR
# BASADA EN EL ODOMETRO ACTIVO. NO SE PUEDEN GUARDAR

    odometer_id = fields.Many2one(
        'fleet.vehicle.odometer.device', 'Odometer', required=True)
    last_odometer = fields.Float(
        string='Last Read', digits=(16, 2), required=True)
    current_odometer = fields.Float(
        string='Current Read', digits=(16, 2), required=True)
    distance = fields.Float(string='Distance', digits=(16, 2), required=True)
    tms_expense_id = fields.Many2one('tms.expense', 'Expense Rec')
    tms_travel_id = fields.Many2one('tms.travel', 'Travel')

    def _check_values(self, cr, uid, ids, context=None):
        for record in self.browse(cr, uid, ids, context=context):
            # print "record.current_odometer: ", record.current_odometer
            # print "record.last_odometer: ", record.last_odometer
            if record.current_odometer <= record.last_odometer:
                return False
            return True

    _constraints = [
        (_check_values,
         'You can not have Current Reading <= Last Reading !',
         ['current_odometer']),
    ]

    def on_change_vehicle(self, vehicle_id):
        res = super(FleetVehicleOdometer, self).on_change_vehicle(
            vehicle_id)
        for vehicle in self.pool.get('fleet.vehicle').browse([vehicle_id]):
            odom_obj = self.pool.get('fleet.vehicle.odometer.device')
            odometer_id = odom_obj.search(
                [('vehicle_id', '=', vehicle_id), ('state', '=', 'active')])
            if odometer_id and odometer_id[0]:
                for odometer in odom_obj.browse(odometer_id):
                    res['value']['odometer_id'] = odometer_id[0]
                    res['value']['last_odometer'] = odometer.odometer_end
                    res['value']['value'] = vehicle.odometer
            else:
                raise Warning(
                    _('Record Warning !'),
                    _('There is no Active Odometer for\
                         vehicle %s') % (vehicle.name)
                )

        return res

    def on_change_current_odometer(
            self, vehicle_id, last_odometer, current_odometer, context=None):
        distance = current_odometer - last_odometer
        accum = self.pool.get('fleet.vehicle').browse(
            [vehicle_id], context=context)[0].odometer + distance
        return {'value':
                {
                    'distance': distance,
                    'value': accum,
                }
                }

    def on_change_distance(
            self, vehicle_id, last_odometer, distance, context=None):
        current_odometer = last_odometer + distance
        accum = self.pool.get('fleet.vehicle').browse(
            [vehicle_id], context=context)[0].odometer + distance
        return {'value':
                {
                    'current_odometer': current_odometer,
                    'value': accum,
                }
                }

    def on_change_value(self, vehicle_id, last_odometer, value, context=None):
        distance = value - self.pool.get('fleet.vehicle').browse(
            [vehicle_id], context=context)[0].odometer
        current_odometer = last_odometer + distance
        return {'value':
                {
                    'current_odometer': current_odometer,
                    'distance': distance,
                }
                }

    def create(self, vals):
        values = vals
        # print "vals: ", vals
        if 'odometer_id' in vals and vals['odometer_id']:
            odom_obj = self.pool.get('fleet.vehicle.odometer.device')
            odometer_end = odom_obj.browse(
                [vals['odometer_id']])[0].odometer_end + vals['distance']
            odom_obj.write(
                [vals['odometer_id']], {'odometer_end': odometer_end})
            return super(FleetVehicleOdometer, self).create(values)

    def create_odometer_log(
            self, expense_id, travel_id, vehicle_id, distance):
        vehicle = self.pool.get('fleet.vehicle').browse([vehicle_id])[0]
        odom_dev_obj = self.pool.get('fleet.vehicle.odometer.device')
        odometer_id = odom_dev_obj.search(
            [('vehicle_id', '=', vehicle_id), ('state', '=', 'active')])
        last_odometer = 0.0
        if odometer_id and odometer_id[0]:
            last_odometer = odom_dev_obj.browse(odometer_id)[0].odometer_end
        else:
            raise Warning(
                _('Could not create Odometer Record!'),
                _('There is no Active Odometer for \
                    Vehicle %s') % (vehicle.name))

        values = {
            'odometer_id': odometer_id[0],
            'vehicle_id': vehicle_id,
            'value': vehicle.odometer + distance,
            'last_odometer': last_odometer,
            'distance': distance,
            'current_odometer': last_odometer + distance,
            'tms_expense_id': expense_id,
            'tms_travel_id': travel_id,
        }
        res = self.create(values)
        # Falta crear un método para actualizar el promedio diario de
        # recorrido de la unidad
        return res

    def unlink_odometer_rec(self, travel_ids, unit_id):
        # print "Entrando a: unlink_odometer_rec "
        unit_obj = self.pool.get('fleet.vehicle')
        # odom_dev_obj = self.pool.get('fleet.vehicle.odometer.device')
        res = self.search(
            [('tms_travel_id', 'in', tuple(travel_ids),),
             ('vehicle_id', '=', unit_id)])
        # print "Registros de lecturas de odometro especificando unidad: ", res
        res1 = self.search([('tms_travel_id', 'in', tuple(travel_ids),)])
        # print "Registros de lecturas de odometro sin especificar unidad: ",
        # res1
        # print "Recorriendo las lecturas de odometro..."
        for odom_rec in self.browse(res):
            # print "===================================="
            # print "Vehiculo: ", odom_rec.vehicle_id.name
            unit_odometer = unit_obj.browse(
                [odom_rec.vehicle_id.id])[0].current_odometer_read
            # print "unit_odometer: ", unit_odometer
            # print "odom_rec.distance: ",odom_rec.distance
            # print "Valor a descontar: ", round(unit_odometer, 2) -
            # round(odom_rec.distance, 2)
            unit_obj.write(
                [unit_id],
                {'current_odometer_read':
                    round(unit_odometer, 2) - round(odom_rec.distance, 2)})
            # print "Después de actualizar el odometro de la unidad..."
            # device_odometer = odom_dev_obj.browse(cr, uid,
            #       [odom_rec.odometer_id.id])[0].odometer_end
            # # print "device_odometer: ", device_odometer
            # # print "device_odometer - odom_rec.distance : ",
            #       round(device_odometer, 2) - round(odom_rec.distance, 2)
            # odom_dev_obj.write(cr, uid, [odom_rec.odometer_id.id],
            #       {'odometer_end': round(device_odometer, 2) -
            #           round(odom_rec.distance, 2)})
            # print "===================================="
        self.unlink(res1)
        return
