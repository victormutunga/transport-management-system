# -*- coding: utf-8 -*-
# © <2012> <Israel Cruz Argil, Argil Consulting>
# © <2016> <Jarsa Sistemas, S.A. de C.V.>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp import api, fields, models
from openerp.exceptions import UserError
from openerp.tools.translate import _


class FleetVehicleLogFuel(models.Model):
    _name = 'fleet.vehicle.log.fuel'
    _inherit = ['fleet.vehicle.log.fuel', 'mail.thread', 'ir.needaction_mixin']

    name = fields.Char()
    travel_id = fields.Many2one('tms.travel', string='Travel')
    employee_id = fields.Many2one(
        'hr.employee',
        string='Driver',
        required=True,
        domain=[('tms_category', '=', 'driver')])
    price_unit = fields.Float(
        # compute=_amount_calculation,
        string='Unit Price',
        store=True)
    product_uom_qty = fields.Float(
        string='Quantity')
    product_uom_id = fields.Many2one(
        'product.uom',
        string='UoM ')
    tax_amount = fields.Float(
        string='Taxes')
    special_tax_amount = fields.Float(
        # compute=_amount_calculation,
        string='IEPS')
    price_total = fields.Float(
        string='Total')
    invoice_id = fields.Many2one(
        'account.invoice',
        'Invoice Record',
        readonly=True,
        domain=[('state', '!=', 'cancel')],)
    invoice_paid = fields.Boolean(
        # compute=_invoiced,
        string='Paid')
    base_id = fields.Many2one(
        'tms.base',
        string='Base',
        required=True)
    notes = fields.Text()
    currency_id = fields.Many2one(
        'res.currency', string='Currency',
        required=True)
    state = fields.Selection(
        [('draft', 'Draft'),
         ('approved', 'Approved'),
         ('confirmed', 'Confirmed'),
         ('closed', 'Closed'),
         ('cancel', 'Cancelled')],
        string='State',
        readonly=True,
        default='draft')
    tax_amount = fields.Float(string='Taxes')
    price_subtotal = fields.Float(
        string="Subtotal",
        compute='_compute_subtotal')
    amount = fields.Float(string="Total", compute="_compute_amount")
    no_travel = fields.Boolean(
        'No Travel', help="Check this if you want to create Fuel Voucher "
        "with no Travel.")
    vendor_id = fields.Many2one('res.partner', required=True)

    @api.multi
    @api.depends('liter', 'price_per_liter')
    def _compute_subtotal(self):
        for rec in self:
            rec.price_subtotal = rec.liter * rec.price_per_liter

    @api.multi
    @api.depends('price_subtotal', 'tax_amount')
    def _compute_amount(self):
        for rec in self:
            rec.amount = rec.price_subtotal + rec.tax_amount

    @api.multi
    def action_approve(self):
        for rec in self:
            if rec.liter == 0:
                raise UserError(
                    _('Liters must be more than 0.'))
            elif rec.price_per_liter == 0:
                raise UserError(
                    _('You neet to assign price per liter'))
            message = _('<b>Fuel Voucher Approved.</b></br><ul>'
                        '<li><b>Supplier: </b>%s</li>'
                        '<li><b>Liters: </b>%s</li>'
                        '<li><b>Price per liter: </b>%s</li>'
                        '<li><b>Driver: </b>%s</li>'
                        '<li><b>Unit: </b>%s</li>'
                        '<li><b>Odometer: </b>%s</li>'
                        '</ul>') % (rec.vendor_id.name, rec.liter,
                                    rec.price_per_liter, rec.employee_id.name,
                                    rec.vehicle_id.name, rec.odometer)
            rec.message_post(body=message)
            rec.state = 'approved'

    @api.multi
    def action_cancel(self):
        for rec in self:
            rec.state = 'draft'

    @api.model
    def create(self, values):
        fuel_log = super(FleetVehicleLogFuel, self).create(values)
        sequence = fuel_log.base_id.fuel_log_sequence_id
        fuel_log.name = sequence.next_by_id()
        return fuel_log
