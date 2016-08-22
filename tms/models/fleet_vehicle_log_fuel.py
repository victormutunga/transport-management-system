# -*- coding: utf-8 -*-
# © <2012> <Israel Cruz Argil, Argil Consulting>
# © <2016> <Jarsa Sistemas, S.A. de C.V.>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp import api, fields, models
from openerp.exceptions import ValidationError
from openerp.tools.translate import _


class FleetVehicleLogFuel(models.Model):
    "Class for Fuel Voucher"
    _name = 'fleet.vehicle.log.fuel'
    _inherit = ['fleet.vehicle.log.fuel', 'mail.thread', 'ir.needaction_mixin']

    name = fields.Char()
    travel_id = fields.Many2one('tms.travel', string='Travel')
    expense_id = fields.Many2one('tms.expense', string='Expense')
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
        string='Invoice Paid',
        compute='_compute_invoiced_paid')
    base_id = fields.Many2one(
        'tms.base',
        string='Base',
        required=True)
    currency_id = fields.Many2one(
        'res.currency', string='Currency',
        required=True,
        default=lambda self: self.env.user.company_id.currency_id)
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
    move_id = fields.Many2one('account.move')

    @api.multi
    @api.depends('product_uom_qty', 'tax_amount', 'price_total')
    def _compute_price_subtotal(self):
        for rec in self:
            rec.price_subtotal = rec.price_total - rec.tax_amount

    @api.multi
    @api.depends('product_uom_qty', 'price_total', 'tax_amount')
    def _compute_price_unit(self):
        for rec in self:
            rec.price_unit = ((rec.price_total - rec.tax_amount -
                               rec.special_tax_amount) /
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
            move_id = rec.move_id.id
            if rec.invoice_id:
                raise ValidationError(
                    _('Could not cancel Fuel Voucher !'),
                    _('This Fuel Voucher is already Invoiced'))
            elif (rec.travel_id and
                  rec.travel_id.state == 'closed'):
                raise ValidationError(
                    _('Could not cancel Fuel Voucher !'),
                    _('This Fuel Voucher is already linked to Travel Expenses'
                      'record'))
            elif move_id:
                move_obj = self.env['account.move']
                if not move_id:
                    raise ValidationError('There is a problem with the Move')
                self.write({'invoice_id': False,
                            'move_id': False})
                message = _('<b>Fuel Voucher Cancelled.</b></br><ul>'
                            '<li><b>Cancelled by: </b>%s</li>'
                            '<li><b>Cancelled at: </b>%s</li>'
                            '</ul>') % (
                                self.env.user.name,
                                fields.Datetime.now())
                rec.message_post(body=message)
                rec.state = 'cancel'
            if move_id:
                move_obj.unlink()

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
            if rec.internal_fuel is True:
                if (rec.base_id.fuelvoucher_product_id.qty_available <
                        rec.product_uom_qty):
                    raise ValidationError(
                        _('Warning! There is not stock'
                          ' for Fuel Voucher %s') % (rec.name))
            else:
                if (rec.product_uom_qty <= 0 or
                        rec.tax_amount <= 0 or
                        rec.price_total <= 0):
                    raise ValidationError(
                        _('Liters, Taxes and Total'
                          ' must be greater than zero.'))
                move_lines = []
                notes = _('* Voucher: %s \n'
                          '* Product: %s \n'
                          '* Travel: %s \n'
                          '* Driver: %s \n'
                          '* Vehicle: %s') % (
                              rec.name,
                              rec.base_id.fuelvoucher_product_id.name,
                              rec.travel_id.name,
                              rec.travel_id.employee_id.name,
                              rec.travel_id.unit_id.name)
                move_obj = self.env['account.move']
                fuel_journal_id = rec.base_id.fuelvoucher_journal_id.id
                fuel_account_id = rec.base_id.account_fuel_id.id
                if not (fuel_journal_id and
                        fuel_account_id and
                        rec.base_id.fuelvoucher_product_id.id):
                    raise ValidationError(
                        _('You need to check the Base'
                          ' Accounts for Fuel Voucher'))
                move_line = (0, 0, {
                    'name': _('Fuel Voucher: %s') % (rec.name),
                    'account_id': fuel_account_id,
                    'journal_id': fuel_journal_id,
                    'narration': notes,
                    'debit': 0.0,
                    'credit': rec.price_subtotal,
                    'fuel_product': rec.base_id.fuelvoucher_product_id.id,
                    'product_uom_id':
                    rec.base_id.fuelvoucher_product_id.uom_id.id,
                    'quantity': rec.product_uom_qty
                })
                move_lines.append(move_line)
                move_line = (0, 0, {
                    'name': _('Fuel rec: %s') % (rec.name),
                    'account_id': fuel_account_id,
                    'journal_id': fuel_journal_id,
                    'debit': rec.price_subtotal,
                    'narration': notes,
                    'credit': 0.0,
                    'fuel_product': rec.base_id.fuelvoucher_product_id.id,
                    'product_uom_id':
                    rec.base_id.fuelvoucher_product_id.uom_id.id,
                    'quantity': rec.product_uom_qty
                })
                move_lines.append(move_line)
                move = {
                    'ref': _('Fuel Voucher: %s') % (rec.name),
                    'narration': rec.notes,
                    'journal_id': fuel_journal_id,
                    'line_ids': [x for x in move_lines],
                    'date': fields.Date.today(),
                }
                move_id = move_obj.create(move)
                if not move_id:
                    raise ValidationError('There is a problem with the Move')
                self.write({'move_id': move_id.id})
            message = _(
                '<b>Fuel Voucher Confirmed.</b></br><ul>'
                '<li><b>Confirmed by: </b>%s</li>'
                '<li><b>Confirmed at: </b>%s</li>'
                '</ul>') % (self.env.user.name, fields.Datetime.now())
            rec.message_post(body=message)
            rec.state = 'confirmed'

    @api.onchange('travel_id')
    def _onchange_travel(self):
        self.base_id = self.travel_id.base_id
        self.vehicle_id = self.travel_id.unit_id
        self.employee_id = self.travel_id.employee_id

    @api.multi
    def create_invoice(self):
        "Returns an open invoice"
        invoice_id = self.env['account.invoice'].create({
            'partner_id': self.vendor_id.id,
            'fiscal_position_id': (
                self.vendor_id.property_account_position_id.id),
            'reference': self.name,
            'currency_id': self.currency_id.id,
            'account_id': self.vendor_id.property_account_payable_id.id,
            'type': 'in_invoice',
            'invoice_line_ids': [(0, 0, {
                'product_id': self.base_id.fuelvoucher_product_id.id,
                'quantity': self.product_uom_qty,
                'price_unit': self.price_unit,
                'invoice_line_tax_ids': [(
                    6, 0,
                    [x.id for x in (
                        self.base_id.fuelvoucher_product_id.supplier_taxes_id)]
                    )],
                'name': self.base_id.fuelvoucher_product_id.name,
                'account_id': (self.base_id.fuelvoucher_product_id.
                               property_account_expense_id.id)}),
                (0, 0, {
                    'product_id': (
                        self.base_id.ieps_product_id.id),
                    'quantity': 1.0,
                    'price_unit': self.special_tax_amount,
                    'name': self.base_id.ieps_product_id.name,
                    'account_id': (
                        self.base_id.ieps_product_id.
                        property_account_expense_id.id)})]
            })
        self.write({'invoice_id': invoice_id.id})

    @api.depends('invoice_id')
    def _compute_invoiced_paid(self):
        for rec in self:
            rec.invoice_paid = (rec.invoice_id.id and
                                rec.invoice_id.state == 'paid')
