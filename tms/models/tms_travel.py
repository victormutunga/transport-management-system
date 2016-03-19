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
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
import time
from datetime import datetime


# Trips / travels
class TmsTravel(models.Model):
    _name = 'tms.travel'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = 'Travels'

    def _route_data(self):
        res = {}
        for record in self.browse(self):
            res[record.id] = {
                'distance_route': 0.0,
                'fuel_efficiency_expected': 0.0,
            }
            distance = record.route_id.distance
            fuel_efficiency_expected = (
                record.route_id.fuel_efficiency_drive_unit
                if not record.trailer1_id
                else record.route_id.fuel_efficiency_1trailer
                if not record.trailer2_id
                else record.route_id.fuel_efficiency_2trailer)
            res[record.id] = {
                'distance_route': distance,
                'fuel_efficiency_expected': fuel_efficiency_expected,
            }
        return res

    def _validate_for_expense_rec(self, ids):
        res = {}
        for record in self.browse(self):
            res[record.id] = {
                'waybill_income': 0.0,
            }

            advance_ok = False
            fuelvoucher_ok = False
            waybill_ok = False
            waybill_income = 0.0

            self.execute("select id from tms_advance where travel_id \
                in %s and state not in ('cancel','confirmed')", (tuple(ids),))
            data_ids = self.fetchall()
            advance_ok = not len(data_ids)

            self.execute("select id from tms_fuelvoucher where travel_id \
                in %s and state not in ('cancel','confirmed')", (tuple(ids),))
            data_ids = self.fetchall()
            fuelvoucher_ok = not len(data_ids)

            self.execute("select id from tms_waybill where travel_id \
                in %s and state not in ('cancel','confirmed')", (tuple(ids),))
            data_ids = self.fetchall()
            waybill_ok = not len(data_ids)

            waybill_income = 0.0
            for waybill in record.waybill_ids:
                waybill_income += waybill.amount_untaxed

            res[record.id] = {
                'advance_ok_for_expense_rec': advance_ok,
                'fuelvoucher_ok_for_expense_rec': fuelvoucher_ok,
                'waybill_ok_for_expense_rec': waybill_ok,
                'waybill_income': waybill_income,
            }
        return res

    def _travel_duration(self):
        res = {}
        for record in self.browse(self):
            res[record.id] = {
                'travel_duration': 0.0,
                'travel_duration_real': 0.0,
            }
            dur1 = (
                datetime.strptime(record.date_end, '%Y-%m-%d %H:%M:%S') -
                datetime.strptime(record.date_start, '%Y-%m-%d %H:%M:%S'))
            dur2 = (
                datetime.strptime(record.date_end_real, '%Y-%m-%d %H:%M:%S') -
                datetime.strptime(record.date_start_real, '%Y-%m-%d %H:%M:%S'))
            x1 = (
                (dur1.days * 24.0 * 60.0 * 60.0) +
                dur1.seconds) / 3600.0 if dur1 else 0.0
            x2 = (
                (dur2.days * 24.0 * 60.0 * 60.0) +
                dur2.seconds) / 3600.0 if dur2 else 0.0
            res[record.id]['travel_duration'] = x1
            res[record.id]['travel_duration_real'] = x2
        return res

    def _get_framework(self):
        res = {}
        for record in self.browse(self):
            if record.trailer2_id.id and record.trailer1_id.id:
                res[record.id] = {
                    'framework': 'Double',
                    'framework_count': 2,
                }
            elif record.trailer1_id.id:
                res[record.id] = {
                    'framework': 'Single',
                    'framework_count': 1,
                }
            else:
                res[record.id] = {
                    'framework': 'Unit',
                    'framework_count': 0,
                }
        return res

    waybill_ids = fields.Many2many(
        'tms.waybill', 'tms_waybill_travel_rel', 'travel_id',
        'waybill_id', 'Waybills')
    default_waybill_id = fields.One2many(
        'tms.waybill', 'travel_id', 'Waybill', readonly=True)
    partner_id = fields.Many2one(
        'default_waybill_id', 'partner_id', relation='res.partner',
        string='Customer', store=True)
    arrival_address_id = fields.Many2one(
        'default_waybill_id', 'arrival_address_id', relation='res.partner',
        string='Arrival Address', store=True)
    expense_driver_factor = fields.One2many(
        'tms.factor', 'travel_id', 'Travel Driver Payment Factors',
        domain=[('category', '=', 'driver')], readonly=False,
        states={'cancel': [('readonly', True)],
                'done': [('readonly', True)]})
    operation_id = fields.Many2one(
        'tms.operation', 'Operation', ondelete='restrict', required=False,
        readonly=False, states={'cancel': [('readonly', True)],
                                'done': [('readonly', True)],
                                'closed': [('readonly', True)]})
    shop_id = fields.Many2one(
        'sale.shop', 'Shop', ondelete='restrict', required=True,
        readonly=False, states={'cancel': [('readonly', True)],
                                'done': [('readonly', True)],
                                'closed': [('readonly', True)]})
    company_id = fields.Many2one(
        'shop_id', 'company_id', relation='res.company', string='Company',
        store=True, readonly=True)
    name = fields.Char('Travel Number', size=64, required=False)
    state = fields.Selection(
        [('draft', 'Pending'), ('progress', 'In Progress'), ('done', 'Done'),
         ('closed', 'Closed'), ('cancel', 'Cancelled')],
        'State', readonly=True, default='draft')
    route_id = fields.Many2one(
        'tms.route', 'Route', required=True,
        states={'cancel': [('readonly', True)],
                'closed': [('readonly', True)]})
    kit_id = fields.Many2one(
        'tms.unit.kit', 'Kit', required=False,
        states={'cancel': [('readonly', True)],
                'closed': [('readonly', True)]})
    unit_id = fields.Many2one(
        'fleet.vehicle', 'Unit', required=True,
        domain=[('fleet_type', '=', 'tractor')],
        states={'cancel': [('readonly', True)],
                'closed': [('readonly', True)]})
    supplier_unit = fields.Boolean(
        'unit_id', 'supplier_unit', string='Supplier Unit', store=True,
        readonly=True)
    supplier_id = fields.Many2one(
        'unit_id', 'supplier_id', relation='res.partner', string='Supplier',
        store=True, readonly=True)
    trailer1_id = fields.Many2one(
        'fleet.vehicle', 'Trailer1', required=False,
        domain=[('fleet_type', '=', 'trailer')],
        states={'cancel': [('readonly', True)],
                'closed': [('readonly', True)]})
    dolly_id = fields.Many2one(
        'fleet.vehicle', 'Dolly', required=False,
        domain=[('fleet_type', '=', 'dolly')],
        states={'cancel': [('readonly', True)],
                'closed': [('readonly', True)]})
    trailer2_id = fields.Many2one(
        'fleet.vehicle', 'Trailer2', required=False,
        domain=[('fleet_type', '=', 'trailer')],
        states={'cancel': [('readonly', True)],
                'closed': [('readonly', True)]})
    employee_id = fields.Many2one(
        'hr.employee', 'Driver', required=True,
        domain=[('tms_category', '=', 'driver')],
        states={'cancel': [('readonly', True)],
                'closed': [('readonly', True)]})
    employee2_id = fields.Many2one(
        'hr.employee', 'Driver Helper', required=False,
        domain=[('tms_category', '=', 'driver')],
        states={'cancel': [('readonly', True)],
                'closed': [('readonly', True)]})
    date = fields.Datetime(
        'Date  registered', required=True,
        states={'cancel': [('readonly', True)],
                'closed': [('readonly', True)]},
        default=(lambda *a: time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)))
    date_start = fields.Datetime(
        'Start Sched', required=False,
        states={'cancel': [('readonly', True)],
                'closed': [('readonly', True)]},
        default=(lambda *a: time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)))
    date_end = fields.Datetime(
        'End Sched', required=False,
        states={'cancel': [('readonly', True)],
                'closed': [('readonly', True)]},
        default=(lambda *a: time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)))
    date_start_real = fields.Datetime(
        'Start Real', required=False,
        states={'cancel': [('readonly', True)],
                'closed': [('readonly', True)]},
        default=(lambda *a: time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)))
    date_end_real = fields.Datetime(
        'End Real', required=False,
        states={'cancel': [('readonly', True)],
                'closed': [('readonly', True)]},
        default=(lambda *a: time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)))
    travel_duration = fields.Float(
        compute=_travel_duration, string='Duration Sched', method=True,
        store=True, digits=(18, 6), multi='travel_duration',
        help="Travel Scheduled duration in hours")
    travel_duration_real = fields.Float(
        compute=_travel_duration, string='Duration Real', method=True,
        store=True, digits=(18, 6), multi='travel_duration',
        help="Travel Real duration in hours")
    distance_route = fields.Float(
        compute=_route_data, string='Route Distance (mi./km)', method=True,
        store={'tms.travel': (lambda self, cr, uid, ids, c={}: ids, None, 10)},
        multi=True)
    fuel_efficiency_expected = fields.Float(
        compute=_route_data, string='Fuel Efficiency Expected', method=True,
        store={'tms.travel': (lambda self, cr, uid, ids, c={}: ids, None, 10)},
        type='float', multi=True, digits=(14, 4))
    advance_ok_for_expense_rec = fields.Boolean(
        compute=_validate_for_expense_rec, string='Advance OK', method=True,
        multi=True)
    # store={
    #     'tms.travel': (lambda self, cr, uid, ids, c={}: ids, ['state',
    #        'fuelvoucher_ids','waybill_ids', 'advance_ids'], 10),
    #     'tms.expense.line': (_get_loan_discounts_from_expense_lines,
    #        ['product_uom_qty', 'price_unit'], 10),
    #     }),
    fuelvoucher_ok_for_expense_rec = fields.Boolean(
        compute=_validate_for_expense_rec, string='Fuel Voucher OK',
        method=True, multi=True)
    waybill_ok_for_expense_rec = fields.Boolean(
        compute=_validate_for_expense_rec, string='Waybill OK',
        method=True, multi=True)
    waybill_income = fields.Float(
        compute=_validate_for_expense_rec, string='Income', method=True,
        digits=(18, 6), store=True, multi=True)
    distance_driver = fields.Float(
        'Distance traveled by driver (mi./km)', required=False, digits=(16, 2),
        states={'cancel': [('readonly', True)],
                'closed': [('readonly', True)]})
    distance_loaded = fields.Float(
        'Distance Loaded (mi./km)', required=False, digits=(16, 2),
        states={'cancel': [('readonly', True)],
                'closed': [('readonly', True)]})
    distance_empty = fields.Float(
        'Distance Empty (mi./km)', required=False, digits=(16, 2),
        states={'cancel': [('readonly', True)],
                'closed': [('readonly', True)]}),
    distance_extraction = fields.Float(
        'Distance Extraction (mi./km)', required=False, digits=(16, 2),
        states={'cancel': [('readonly', True)],
                'closed': [('readonly', True)]})
    fuel_efficiency_travel = fields.Float(
        'Fuel Efficiency Travel', required=False, digits=(14, 4),
        states={'cancel': [('readonly', True)],
                'closed': [('readonly', True)]})
    fuel_efficiency_extraction = fields.Float(
        'Fuel Efficiency Extraction', required=False, digits=(14, 4),
        states={'cancel': [('readonly', True)],
                'closed': [('readonly', True)]})
    departure_id = fields.Many2one(
        'route_id', 'departure_id', relation='tms.place', string='Departure',
        store=True, readonly=True)
    arrival_id = fields.Many2one(
        'route_id', 'arrival_id', relation='tms.place', string='Arrival',
        store=True, readonly=True)
    notes = fields.Text(
        'Descripción', required=False,
        states={'cancel': [('readonly', True)],
                'closed': [('readonly', True)]})
    fuelvoucher_ids = fields.One2many(
        'tms.fuelvoucher', 'travel_id', string='Fuel Vouchers',
        states={'cancel': [('readonly', True)],
                'closed': [('readonly', True)]})
    advance_ids = fields.One2many(
        'tms.advance', 'travel_id', string='Advances',
        states={'cancel': [('readonly', True)],
                'closed': [('readonly', True)]})
    framework = fields.Char(
        compute=_get_framework, string='Framework', method=True, store=True,
        size=15, multi='framework')
    framework_count = fields.Integer(
        compute=_get_framework, string='Framework Count', method=True,
        store=True, multi='framework'),
    framework_supplier = fields.Selection(
        [('Unit', 'Unit'), ('Single', 'Single'), ('Double', 'Double')],
        'Framework', states={'cancel': [('readonly', True)],
                             'closed': [('readonly', True)]})
    create_uid = fields.Many2one('res.users', 'Created by', readonly=True)
    create_date = fields.datetime('Creation Date', readonly=True, select=True)
    cancelled_by = fields.Many2one('res.users', 'Cancelled by', readonly=True)
    date_cancelled = fields.datetime('Date Cancelled', readonly=True)
    dispatched_by = fields.Many2one(
        'res.users', 'Dispatched by', readonly=True)
    date_dispatched = fields.datetime('Date Dispatched', readonly=True)
    done_by = fields.Many2one('res.users', 'Ended by', readonly=True)
    date_done = fields.datetime('Date Ended', readonly=True)
    closed_by = fields.Many2one('res.users', 'Closed by', readonly=True)
    date_closed = fields.datetime('Date Closed', readonly=True)
    drafted_by = fields.Many2one('res.users', 'Drafted by', readonly=True),
    date_drafted = fields.datetime('Date Drafted', readonly=True),
    user_id = fields.Many2one(
        'res.users', 'Salesman', select=True, readonly=False,
        states={'cancel': [('readonly', True)],
                'closed': [('readonly', True)]},
        default=(lambda obj, cr, uid, context: uid))
    parameter_distance = fields.Integer(
        'Distance Parameter',
        help="1 = Travel, 2 = Travel Expense, 3 = Manual, 4 = Tyre",
        default=(lambda s, cr, uid, c: int(
            s.pool.get('ir.config_parameter').get_param(
                cr, uid,
                'tms_property_update_vehicle_distance', context=c)[0])))
    expense_ids = fields.Many2many(
        'tms.expense', 'tms_expense_travel_rel', 'travel_id',
        'expense_id', 'Expense Record')
    expense_ids2 = fields.Many2many(
        'tms.expense', 'tms_expense_travel_rel2', 'travel_id',
        'expense_id', 'Expense Record for Driver Helper')
    expense_id = fields.Many2one(
        'tms.expense', 'Expense Record', required=False, readonly=True)
    expense2_id = fields.Many2one(
        'tms.expense', 'Expense Record for Driver Helper', required=False,
        readonly=True)
    event_ids = fields.One2many('tms.event', 'travel_id', string='Events'),

    _sql_constraints = [
        ('name_uniq', 'unique(shop_id,name)',
            'Travel number must be unique !'),
    ]
    _order = "date desc"

    def _check_drivers_change(self):
        for record in self.browse(self):
            travel_id = record.id
            employee1_id = (record.employee_id.id if
                            record.employee_id.id else 0)
            employee2_id = (record.employee2_id.id if
                            record.employee2_id.id else 0)
            self.execute("""
                select id from tms_advance where travel_id = %s and state \
                    not in ('cancel') and employee_id <> %s and \
                    not driver_helper
                union
                select id from tms_advance where travel_id = %s and state \
                    not in ('cancel') and employee_id <> %s and \
                    driver_helper
                union
                select id from tms_fuelvoucher where travel_id = %s and \
                    state not in ('cancel') and employee_id <> %s and \
                    not driver_helper
                union
                select id from tms_fuelvoucher where travel_id = %s and \
                    state not in ('cancel') and employee_id <> %s and \
                    driver_helper
                """, (travel_id, employee1_id,
                      travel_id, employee2_id,
                      travel_id, employee1_id,
                      travel_id, employee2_id))
            data_ids = self.fetchall()
            # print data_ids
            return (not len(data_ids))

    _constraints = [
        (
            _check_drivers_change,
            'You can not modify Driver and/or Driver Helper if there are \
                linked records (Fuel vouchers, Advances, etc).',
            ['employee_id', 'employee2_id']),
    ]

    def onchange_unit_id(self, unit_id):
        if not unit_id:
            return {}
        vehicle = self.pool.get('fleet.vehicle').browse(unit_id)
        return {'value': {'supplier_id': vehicle.supplier_id.id}}

    def onchange_kit_id(self, kit_id):
        if not kit_id:
            return {}
        kit = self.pool.get('tms.unit.kit').browse(kit_id)
        return {'value': {
            'unit_id': kit.unit_id.id,
            'trailer1_id': kit.trailer1_id.id,
            'dolly_id': kit.dolly_id.id,
            'trailer2_id': kit.trailer2_id.id,
            'employee_id': kit.employee_id.id}
        }

    def get_factors_from_route(self):
        if len(self):
            factor_obj = self.pool.get('tms.factor')
            # factor_ids = factor_obj.search(
            #     [('travel_id', '=', self[0]), ('control', '=', 1)],
            #     context=None)
            # if factor_ids:
            # res = factor_obj.unlink(factor_ids)
            # factors = []
            for factor in self.browse(self)[0].route_id.expense_driver_factor:
                x = {
                    'name': factor.name,
                    'category': 'driver',
                    'factor_type': factor.factor_type,
                    'range_start': factor.range_start,
                    'range_end': factor.range_end,
                    'factor': factor.factor,
                    'fixed_amount': factor.fixed_amount,
                    'mixed': factor.mixed,
                    'factor_special_id': factor.factor_special_id.id,
                    'travel_id': self[0],
                    'control': True,
                    'driver_helper': factor.driver_helper,
                }
                print "x: ", x
                factor_obj.create(x)
        return True

    def write(self):
        super(TmsTravel, self).write(self)
        if 'state' in self and self['state'] not in (
                'cancel', 'done', 'closed'):
            self.get_factors_from_route(self)
        return True

    def onchange_route_id(
            self, route_id, unit_id, trailer1_id, dolly_id, trailer2_id):
        if not route_id:
            return {'value': {
                'distance_route': 0.00,
                'distance_extraction': 0.0,
                'fuel_efficiency_expected': 0.00}}
        val = {}
        route = self.pool.get('tms.route').browse(route_id)
        distance = route.distance
        fuel_efficiency_expected = (
            route.fuel_efficiency_drive_unit
            if not trailer1_id
            else route.fuel_efficiency_1trailer
            if not trailer2_id
            else route.fuel_efficiency_2trailer)

        factors = []
        for factor in route.expense_driver_factor:
            x = (0, 0, {
                'name': factor.name,
                'category': 'driver',
                'factor_type': factor.factor_type,
                'range_start': factor.range_start,
                'range_end': factor.range_end,
                'factor': factor.factor,
                'fixed_amount': factor.fixed_amount,
                'mixed': factor.mixed,
                'factor_special_id': factor.factor_special_id.id,
                'control': True,
                'driver_helper': factor.driver_helper,
                # 'travel_id'     : ids[0],
            })
            factors.append(x)

        val = {
            'distance_route': distance,
            'distance_extraction': distance,
            'fuel_efficiency_expected': fuel_efficiency_expected,
            'expense_driver_factor': factors,
        }
        return {'value': val}

    def onchange_dates(
            self, date_start, date_end, date_start_real, date_end_real):
        if (not date_start or not date_end or not
                date_start_real or not date_end_real):
            return {'value': {
                'travel_duration': 0.0,
                'travel_duration_real': 0.0}}
        dur1 = (datetime.strptime(date_end, '%Y-%m-%d %H:%M:%S') -
                datetime.strptime(date_start, '%Y-%m-%d %H:%M:%S'))
        dur2 = (datetime.strptime(date_end_real, '%Y-%m-%d %H:%M:%S') -
                datetime.strptime(date_start_real, '%Y-%m-%d %H:%M:%S'))
        x1 = ((dur1.days * 24.0 * 60.0 * 60.0) + dur1.seconds) / 3600.0
        x2 = ((dur2.days * 24.0 * 60.0 * 60.0) + dur2.seconds) / 3600.0
        val = {
            'travel_duration': x1,
            'travel_duration_real': x2,
        }
        return {'value': val}

    def create(self):
        shop = self.pool.get('sale.shop').browse(self['shop_id'])
        seq_id = shop.tms_travel_seq.id
        if shop.tms_travel_seq:
            seq_number = self.pool.get('ir.sequence').get_id(seq_id)
            self['name'] = seq_number
        else:
            raise Warning(
                _('Travel Sequence Error !'),
                _('You have not defined Travel Sequence for shop ' +
                    shop.name))
        return super(TmsTravel, self).create(self)

    def action_cancel_draft(self):
        if not len(self):
            return False
        self.write({
            'state': 'draft',
            'drafted_by': self,
            'date_drafted': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)})
        return True

    def action_cancel(self):
        for travel in self.browse(self):
            for fuelvouchers in travel.fuelvoucher_ids:
                if fuelvouchers.state not in ('cancel'):
                    raise Warning(
                        _('Could not cancel Travel !'),
                        _('You must first cancel all Fuel Vouchers \
                            attached to this Travel.'))
            for waybills in travel.waybill_ids:
                if waybills.state not in ('cancel'):
                    raise Warning(
                        _('Could not cancel Travel !'),
                        _('You must first cancel all Waybills attached \
                            to this Travel.'))
            for advances in travel.advance_ids:
                if advances.state not in ('cancel'):
                    raise Warning(
                        _('Could not cancel Travel !'),
                        _('You must first cancel all Advances for Drivers \
                            attached to this Travel.'))

            if not travel.parameter_distance:
                    raise Warning(
                        _('Could not Confirm Expense Record !'),
                        _('Parameter to determine Vehicle distance update \
                            from does not exist.'))
            elif travel.parameter_distance == 2:
                # Revisamos el parametro (tms_property_update_vehicle_distance)
                # donde se define donde se actualizan los kms/millas a las
                # unidades
                self.pool.get('fleet.vehicle.odometer').unlink_odometer_rec(
                    self)

        self.write({'state': 'cancel', 'cancelled_by': self,
                    'date_cancelled':
                    time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)})

        return True

    def action_dispatch(self):
        for travel in self.browse(self):
            unit = travel.unit_id.id
            travels = self.pool.get('tms.travel')
            travel_id = travels.search(
                [('unit_id', '=', unit), ('state', '=', 'progress')])
            if travel_id:
                raise Warning(
                    _('Could not dispatch Travel !'),
                    _('There is already a Travel in progress with Unit ' +
                        travel.unit_id.name))
        self.write({
            'state': 'progress',
            'dispatched_by': self,
            'date_dispatched': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
            'date_start_real': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)})
        return True

    def action_end(self):
        for travel in self.browse(self):
            if not travel.parameter_distance:
                raise Warning(
                    _('Could not End Travel !'),
                    _('Parameter to determine Vehicle distance origin does \
                        not exist.'))
            elif travel.parameter_distance == 1:
                # parametro (tms_property_update_vehicle_distance) donde se
                # define donde se actualizan los kms/millas a las unidades
                odom_obj = self.pool.get('fleet.vehicle.odometer')
                xdistance = travel.distance_extraction
                odom_obj.create_odometer_log(
                    False, travel.id, travel.unit_id.id, xdistance)
                if travel.trailer1_id and travel.trailer1_id.id:
                    odom_obj.create_odometer_log(
                        False, travel.id, travel.trailer1_id.id, xdistance)
                if travel.dolly_id and travel.dolly_id.id:
                    odom_obj.create_odometer_log(
                        False, travel.id, travel.dolly_id.id, xdistance)
                if travel.trailer2_id and travel.trailer2_id.id:
                    odom_obj.create_odometer_log(
                        False, travel.id, travel.trailer2_id.id, xdistance)
        self.write({
            'state': 'done',
            'ended_by': self,
            'date_ended': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
            'date_end_real': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)})
        return True
