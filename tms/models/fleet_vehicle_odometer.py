# -*- coding: utf-8 -*-
# © <2012> <Israel Cruz Argil, Argil Consulting>
# © <2016> <Jarsa Sistemas, S.A. de C.V.>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp import fields, models
# from openerp.tools.translate import _

# Vehicle Odometer records


class FleetVehicleOdometer(models.Model):
    _inherit = ['fleet.vehicle.odometer']
    _name = 'fleet.vehicle.odometer'
#  PENDIENTES
# - CALCULAR LA DISTANCIA RECORRIDA ENTRE EL REGISTRO ACTUAL Y EL ANTERIOR
# BASADA EN EL ODOMETRO ACTIVO. NO SE PUEDEN GUARDAR

    # odometer_id = fields.Many2one(
    #     'fleet.vehicle.odometer.device',
    #     string='Odometer',
    #     required=True)
    last_odometer = fields.Float(
        string='Last Read',
        required=True)
    current_odometer = fields.Float(
        string='Current Read',
        required=True)
    distance = fields.Float(
        string='Distance',
        required=True)
    # tms_expense_id = fields.Many2one('tms.expense', 'Expense Rec')
    tms_travel_id = fields.Many2one('tms.travel', string='Travel')

    # _constraints = [
    #     (_check_values,
    #      'You can not have Current Reading <= Last Reading !',
    #      ['current_odometer']),
    # ]
