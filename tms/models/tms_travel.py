# -*- coding: utf-8 -*-
# © <2012> <Israel Cruz Argil, Argil Consulting>
# © <2016> <Jarsa Sistemas, S.A. de C.V.>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


# Trips / travels
class TmsTravel(models.Model):
    _name = 'tms.travel'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = 'Travels'
    _order = "date desc"

    waybill_ids = fields.Many2many(
        'tms.waybill', string='Waybills')
    expense_driver_factor = fields.One2many(
        'tms.factor', 'travel_id', string='Travel Driver Payment Factors',
        domain=[('category', '=', 'driver')],
        states={'cancel': [('readonly', True)],
                'done': [('readonly', True)]})
    name = fields.Char('Travel Number')
    state = fields.Selection(
        [('draft', 'Pending'), ('progress', 'In Progress'), ('done', 'Done'),
         ('closed', 'Closed'), ('cancel', 'Cancelled')],
        'State', readonly=True, default='draft')
    route_id = fields.Many2one(
        'tms.route', 'Route', required=True,
        states={'cancel': [('readonly', True)],
                'closed': [('readonly', True)]})
    travel_duration = fields.Float(
        # compute=_compute_travel_duration,
        string='Duration Sched',
        help='Travel Scheduled duration in hours')
    travel_duration_real = fields.Float(
        # compute=_travel_duration,
        string='Duration Real', help="Travel Real duration in hours")
    distance_route = fields.Float(
        # compute=_route_data,
        string='Route Distance (mi./km)')
    fuel_efficiency_expected = fields.Float(
        # compute=_route_data,
        string='Fuel Efficiency Expected')
    kit_id = fields.Many2one(
        'tms.unit.kit', 'Kit',
        states={'cancel': [('readonly', True)],
                'closed': [('readonly', True)]})
    unit_id = fields.Many2one(
        'fleet.vehicle', 'Unit',
        domain=[('fleet_type', '=', 'tractor')],
        states={'cancel': [('readonly', True)],
                'closed': [('readonly', True)]})
    trailer1_id = fields.Many2one(
        'fleet.vehicle', 'Trailer1',
        domain=[('fleet_type', '=', 'trailer')],
        states={'cancel': [('readonly', True)],
                'closed': [('readonly', True)]})
    dolly_id = fields.Many2one(
        'fleet.vehicle', 'Dolly',
        domain=[('fleet_type', '=', 'dolly')],
        states={'cancel': [('readonly', True)],
                'closed': [('readonly', True)]})
    trailer2_id = fields.Many2one(
        'fleet.vehicle', 'Trailer2',
        domain=[('fleet_type', '=', 'trailer')],
        states={'cancel': [('readonly', True)],
                'closed': [('readonly', True)]})
    employee_id = fields.Many2one(
        'hr.employee', 'Driver', required=True,
        domain=[('tms_category', '=', 'driver')],
        states={'cancel': [('readonly', True)],
                'closed': [('readonly', True)]})
    date = fields.Datetime(
        'Date  registered', required=True,
        states={'cancel': [('readonly', True)],
                'closed': [('readonly', True)]},
        default=(fields.Datetime.now))
    date_start = fields.Datetime(
        'Start Sched',
        states={'cancel': [('readonly', True)],
                'closed': [('readonly', True)]},
        default=(fields.Datetime.now))
    date_end = fields.Datetime(
        'End Sched',
        states={'cancel': [('readonly', True)],
                'closed': [('readonly', True)]},
        default=(fields.Datetime.now))
    date_start_real = fields.Datetime(
        'Start Real',
        states={'cancel': [('readonly', True)],
                'closed': [('readonly', True)]},
        default=(fields.Datetime.now))
    date_end_real = fields.Datetime(
        'End Real',
        states={'cancel': [('readonly', True)],
                'closed': [('readonly', True)]},
        default=(fields.Datetime.now))
    distance_driver = fields.Float(
        'Distance traveled by driver (mi./km)',
        states={'cancel': [('readonly', True)],
                'closed': [('readonly', True)]})
    distance_loaded = fields.Float(
        'Distance Loaded (mi./km)',
        states={'cancel': [('readonly', True)],
                'closed': [('readonly', True)]})
    distance_empty = fields.Float(
        'Distance Empty (mi./km)',
        states={'cancel': [('readonly', True)],
                'closed': [('readonly', True)]})
    distance_extraction = fields.Float(
        'Distance Extraction (mi./km)',
        states={'cancel': [('readonly', True)],
                'closed': [('readonly', True)]})
    fuel_efficiency_travel = fields.Float(
        'Fuel Efficiency Travel',
        states={'cancel': [('readonly', True)],
                'closed': [('readonly', True)]})
    fuel_efficiency_extraction = fields.Float(
        'Fuel Efficiency Extraction',
        states={'cancel': [('readonly', True)],
                'closed': [('readonly', True)]})
    departure_id = fields.Many2one(
        'tms.place',
        related='route_id.departure_id',
        readonly=True)
    fuel_log_ids = fields.One2many(
        'fleet.vehicle.log.fuel', 'travel_id', string='Fuel Vouchers',
        states={'cancel': [('readonly', True)],
                'closed': [('readonly', True)]})
    advance_ids = fields.One2many(
        'tms.advance', 'travel_id', string='Advances',
        states={'cancel': [('readonly', True)],
                'closed': [('readonly', True)]})
    arrival_id = fields.Many2one(
        'tms.place',
        related='route_id.arrival_id',
        readonly=True)
    notes = fields.Text(
        'Descripción',
        states={'cancel': [('readonly', True)],
                'closed': [('readonly', True)]})
    user_id = fields.Many2one(
        'res.users', 'Salesman',
        states={'cancel': [('readonly', True)],
                'closed': [('readonly', True)]})
    expense_id = fields.Many2one(
        'tms.expense', 'Expense Record', readonly=True)
    event_ids = fields.One2many('tms.event', 'travel_id', string='Events')

    _sql_constraints = [
        ('name_uniq', 'unique(name)',
            'Travel number must be unique !'),
    ]
