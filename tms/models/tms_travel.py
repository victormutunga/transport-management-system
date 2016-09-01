# -*- coding: utf-8 -*-
# © <2012> <Israel Cruz Argil, Argil Consulting>
# © <2016> <Jarsa Sistemas, S.A. de C.V.>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import _, api, fields, models
from openerp.exceptions import ValidationError


class TmsTravel(models.Model):
    _name = 'tms.travel'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = 'Travel'
    _order = "date desc"
    waybill_ids = fields.Many2many(
        'tms.waybill', string='Waybills')
    driver_factor_ids = fields.One2many(
        'tms.factor', 'travel_id', string='Travel Driver Payment Factors',
        domain=[('category', '=', 'driver')],
        states={'cancel': [('readonly', True)],
                'done': [('readonly', True)]})
    name = fields.Char('Travel Number')
    state = fields.Selection(
        [('draft', 'Pending'), ('progress', 'In Progress'), ('done', 'Done'),
         ('cancel', 'Cancelled')],
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
        'tms.unit.kit', 'Kit')
    unit_id = fields.Many2one(
        'fleet.vehicle', 'Unit',
        domain=[('fleet_type', '=', 'tractor')],
        required=True)
    trailer1_id = fields.Many2one(
        'fleet.vehicle', 'Trailer1',
        domain=[('fleet_type', '=', 'trailer')])
    dolly_id = fields.Many2one(
        'fleet.vehicle', 'Dolly',
        domain=[('fleet_type', '=', 'dolly')])
    trailer2_id = fields.Many2one(
        'fleet.vehicle', 'Trailer2',
        domain=[('fleet_type', '=', 'trailer')])
    employee_id = fields.Many2one(
        'hr.employee', 'Driver', required=True,
        domain=[('driver', '=', True)])
    date = fields.Datetime(
        'Date  registered', required=True,
        default=(fields.Datetime.now))
    date_start = fields.Datetime(
        'Start Sched',
        default=(fields.Datetime.now))
    date_end = fields.Datetime(
        'End Sched',
        default=(fields.Datetime.now))
    date_start_real = fields.Datetime(
        'Start Real')
    date_end_real = fields.Datetime(
        'End Real')
    distance_driver = fields.Float(
        'Distance traveled by driver (mi./km)')
    distance_loaded = fields.Float(
        'Distance Loaded (mi./km)')
    distance_empty = fields.Float(
        'Distance Empty (mi./km)')
    distance_extraction = fields.Float(
        'Distance Extraction (mi./km)')
    fuel_efficiency_travel = fields.Float(
        'Fuel Efficiency Travel')
    fuel_efficiency_extraction = fields.Float(
        'Fuel Efficiency Extraction')
    departure_id = fields.Many2one(
        'tms.place',
        related='route_id.departure_id',
        readonly=True)
    fuel_log_ids = fields.One2many(
        'fleet.vehicle.log.fuel', 'travel_id', string='Fuel Vouchers')
    advance_ids = fields.One2many(
        'tms.advance', 'travel_id', string='Advances')
    arrival_id = fields.Many2one(
        'tms.place',
        related='route_id.arrival_id',
        readonly=True)
    notes = fields.Text(
        'Descripción')
    user_id = fields.Many2one(
        'res.users', 'Responsable',
        default=lambda self: self.env.user)
    expense_id = fields.Many2one(
        'tms.expense', 'Expense Record', readonly=True)
    event_ids = fields.One2many('tms.event', 'travel_id', string='Events')
    is_available = fields.Boolean(
        compute='_is_available',
        string='Travel available')
    base_id = fields.Many2one('tms.base', 'Base')

    @api.onchange('kit_id')
    def _onchange_kit(self):
        self.unit_id = self.kit_id.unit_id
        self.trailer2_id = self.kit_id.trailer2_id
        self.trailer1_id = self.kit_id.trailer1_id
        self.dolly_id = self.kit_id.dolly_id
        self.employee_id = self.kit_id.employee_id

    @api.onchange('route_id')
    def _onchange_route(self):
        self.driver_factor_ids = self.route_id.driver_factor_ids

    @api.multi
    def action_draft(self):
        self.state = "draft"

    @api.multi
    def action_progress(self):
        travels = self.search(
            [('state', '=', 'progress'), '|',
             ('employee_id', '=', self.employee_id.id),
             ('unit_id', '=', self.unit_id.id)])
        if len(travels) >= 1:
            raise ValidationError(
                _('The unit or driver are already in use!'))
        self.state = "progress"
        self.date_start_real = fields.Datetime.now()
        self.message_post('Travel Dispatched')

    @api.multi
    def action_done(self):
        self.state = "done"
        self.date_end_real = fields.Datetime.now()
        self.message_post('Travel Finished')

    @api.multi
    def action_cancel(self):
        advances = self.search([
            '|',
            ('fuel_log_ids', '!=', 'cancel'),
            ('advance_ids', '!=', 'cancel')])
        if len(advances) >= 1:
            raise ValidationError(
                _('If you want to cancel this travel, you must cancel the fuel'
                  ' logs or the advances attached to this travel'))
        self.state = "cancel"
        self.message_post('Travel Cancelled')

    @api.model
    def create(self, values):
        travel = super(TmsTravel, self).create(values)
        sequence = travel.base_id.travel_sequence_id
        travel.name = sequence.next_by_id()
        return travel

    @api.depends()
    def _is_available(self):
        models = ['tms.advance', 'fleet.vehicle.log.fuel', 'tms.waybill']
        advances = len(self.advance_ids)
        fuel_vehicle = len(self.fuel_log_ids)
        count = 0
        for model in models:
            if model == 'tms.advance' or model == 'fleet.vehicle.log.fuel':
                object_ok = len(self.env[model].search(
                    [('state', '=', 'confirmed'),
                     ('travel_id', '=', self.id)]))
                if (model == 'tms.advance' and
                        advances == object_ok or advances == 0):
                    count += 1
                elif (model == 'fleet.vehicle.log.fuel' and
                        fuel_vehicle == object_ok or fuel_vehicle == 0):
                    count += 1
            if model == 'tms.waybill':
                object_ok = len(self.env[model].search(
                    [('state', '=', 'confirmed'),
                     ('travel_ids', 'in', self.id)]))
                if len(self.waybill_ids) == object_ok:
                    count += 1
        if count == 3:
            self.is_available = True
