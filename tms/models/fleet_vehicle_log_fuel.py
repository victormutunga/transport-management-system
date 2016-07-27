# -*- coding: utf-8 -*-
# © <2012> <Israel Cruz Argil, Argil Consulting>
# © <2016> <Jarsa Sistemas, S.A. de C.V.>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp import api, fields, models
from openerp.exceptions import UserError
from openerp.tools.translate import _


class FleetVehicleLogFuel(models.Model):
    "Class for Fuel Voucher"
    _name = 'fleet.vehicle.log.fuel'
    _inherit = ['fleet.vehicle.log.fuel', 'mail.thread', 'ir.needaction_mixin']

    name = fields.Char()
    travel_id = fields.Many2one('tms.travel', string='Travel')
    employee_id = fields.Many2one(
        'hr.employee',
        string='Driver',
        required=True,
        domain=[('tms_category', '=', 'driver')])
    product_uom_id = fields.Many2one(
        'product.uom',
        string='UoM ',
        required=True)
    product_uom_qty = fields.Float(
        string='Liters', required=True, default=1.0)
    tax_amount = fields.Float(
        string='Taxes', required=True)
    price_total = fields.Float(
        string='Total', required=True)
    special_tax_amount = fields.Float(
        compute="_compute_special_tax_amount",
        string='IEPS')
    price_unit = fields.Float(
        compute='_compute_price_unit',
        string='Unit Price')
    price_subtotal = fields.Float(
        string="Subtotal",
        compute='_compute_price_subtotal')
    invoice_id = fields.Many2one(
        'account.invoice',
        'Invoice',
        readonly=True,
        domain=[('state', '!=', 'cancel')],)
    invoice_paid = fields.Boolean(
        compute='_invoiced',
        string='Invoice Paid')
    base_id = fields.Many2one(
        'tms.base',
        string='Base',
        required=True)
    currency_id = fields.Many2one(
        'res.currency', string='Currency',
        required=True)
    notes = fields.Char(
        states={'cancel': [('readonly', True)],
                'confirmed': [('readonly', True)],
                'closed': [('readonly', True)]})
    state = fields.Selection(
        [('draft', 'Draft'),
         ('approved', 'Approved'),
         ('confirmed', 'Confirmed'),
         ('cancel', 'Cancelled')],
        string='State',
        readonly=True,
        default='draft')
    no_travel = fields.Boolean(
        'No Travel', help="Check this if you want to create Fuel Voucher "
        "with no Travel.")
    vendor_id = fields.Many2one('res.partner', required=True)
    internal_fuel = fields.Boolean(domain=[('state', '=', 'draft')])

    @api.multi
    @api.depends('product_uom_qty', 'tax_amount', 'price_total')
    def _compute_price_subtotal(self):
        for rec in self:
            rec.price_subtotal = rec.price_total - rec.tax_amount

    @api.multi
    @api.depends('product_uom_qty', 'price_total', 'tax_amount')
    def _compute_price_unit(self):
        for rec in self:
            rec.price_unit = ((rec.price_total - rec.tax_amount) /
                              rec.product_uom_qty)

    @api.multi
    @api.depends('product_uom_qty', 'tax_amount')
    def _compute_special_tax_amount(self):
        for rec in self:
            rec.special_tax_amount = rec.price_subtotal - ((
                rec.tax_amount / 16) * 100)

    @api.multi
    def action_approved(self):
        "Action for Approve"
        for rec in self:
            message = _('<b>Fuel Voucher Approved.</b></br><ul>'
                        '<li><b>Approved by: </b>%s</li>'
                        '<li><b>Approved at: </b>%s</li>'
                        '</ul>') % (self.env.user.name, fields.Datetime.now())
            rec.message_post(body=message)
            rec.state = 'approved'

    @api.multi
    def action_cancel(self):
        "Action for Cancel"
        for rec in self:
            message = _('<b>Fuel Voucher Cancelled.</b></br><ul>'
                        '<li><b>Cancelled by: </b>%s</li>'
                        '<li><b>Cancelled at: </b>%s</li>'
                        '</ul>') % (self.env.user.name, fields.Datetime.now())
            rec.message_post(body=message)
            rec.state = 'cancel'

    @api.model
    def create(self, values):
        "Sequence Method"
        fuel_log = super(FleetVehicleLogFuel, self).create(values)
        sequence = fuel_log.base_id.fuel_log_sequence_id
        fuel_log.name = sequence.next_by_id()
        return fuel_log

    @api.multi
    def set_2_draft(self):
        "Back to Draft"
        for rec in self:
            message = _(
                '<b>Fuel Voucher Draft.</b></br><ul>'
                '<li><b>Drafted by: </b>%s</li>'
                '<li><b>Drafted at: </b>%s</li>'
                '</ul>') % (self.env.user.name, fields.Datetime.now())
            rec.message_post(body=message)
            rec.state = 'draft'

    @api.multi
    def action_confirm(self):
        "Confirm Action"
        for rec in self:
            if rec.internal_fuel is not True:
                if (rec.product_uom_qty <= 0 or
                        rec.tax_amount <= 0 or
                        rec.price_total <= 0):
                    raise UserError(
                        _('Liters, Taxes and Total'
                          ' must be greater than zero.'))
                message = _(
                    '<b>Fuel Voucher Confirmed.</b></br><ul>'
                    '<li><b>Confirmed by: </b>%s</li>'
                    '<li><b>Confirmed at: </b>%s</li>'
                    '</ul>') % (self.env.user.name, fields.Datetime.now())
                rec.message_post(body=message)
                rec.state = 'confirmed'

    @api.multi
    def _invoiced(self):
        "Invoice "
        for rec in self:
            rec.invoice_paid = (rec.invoice_id and
                                rec.invoice_id.state == 'paid')
