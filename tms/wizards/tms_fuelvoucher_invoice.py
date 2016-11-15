# -*- coding: utf-8 -*-
# © <2012> <Israel Cruz Argil, Argil Consulting>
# © <2016> <Jarsa Sistemas, S.A. de C.V.>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp import _, api, exceptions, models


class TmsFuelvoucherInvoice(models.TransientModel):

    _name = 'tms.fuelvoucher.invoice'
    _description = 'Make Invoices from Fuel Vouchers'

    @api.multi
    def make_fuel_invoices(self):
        active_ids = self.env['fleet.vehicle.log.fuel'].browse(
            self._context.get('active_ids'))
        if not active_ids:
            return {}

        partner_ids = []
        total = 0.0
        control = 0
        lines = []
        for fuel in active_ids:
            if len(fuel.invoice_id) > 0:
                raise exceptions.ValidationError(
                    _('The fuel already has an invoice'))
            else:
                if (fuel.state in ('confirmed', 'closed') and not
                        fuel.invoice_paid):
                    partner_address = fuel.vendor_id.address_get(
                        ['invoice', 'contact']).get('invoice', False)
                    if not partner_address:
                        raise exceptions.ValidationError(
                            _('You must configure the home address for the'
                              ' Customer.'))
                    partner_ids.append(partner_address)
                    currency = fuel.currency_id
                    total += currency.compute(fuel.price_total,
                                              self.env.user.currency_id)
                else:
                    raise exceptions.ValidationError(
                        _('The fuels must be in confirmed / closed state'
                          ' and unpaid.'))
                lines.append(
                    (0, 0, {
                        'product_id': (
                            fuel.base_id.fuelvoucher_product_id.id),
                        'quantity': fuel.product_uom_qty,
                        'price_unit': fuel.price_unit,
                        'invoice_line_tax_ids': [(
                            6, 0,
                            [x.id for x in (
                                fuel.base_id.fuelvoucher_product_id.
                                supplier_taxes_id)]
                        )],
                        'name': fuel.base_id.fuelvoucher_product_id.name,
                        'account_id': (
                            fuel.base_id.fuelvoucher_product_id.
                            property_account_expense_id.id)}))
                lines.append((0, 0, {
                    'product_id': (
                        fuel.base_id.ieps_product_id.id),
                    'quantity': 1.0,
                    'price_unit': fuel.special_tax_amount,
                    'name': fuel.base_id.ieps_product_id.name,
                    'account_id': (
                        fuel.base_id.ieps_product_id.
                        property_account_expense_id.id)})
                )
        for partner_id in partner_ids:
            if control == 0:
                old_partner = partner_id
                current_partner = partner_id
                control = 1
            else:
                current_partner = partner_id
            if old_partner != current_partner:
                raise exceptions.ValidationError(
                    _('The fuels must be of the same customer. '
                      'Please check it.'))
            else:
                old_partner = partner_id

        invoice_id = self.env['account.invoice'].create({
            'partner_id': fuel.vendor_id.id,
            'fiscal_position_id': (
                fuel.vendor_id.property_account_position_id.id),
            'reference': fuel.name,
            'currency_id': fuel.currency_id.id,
            'account_id': (
                fuel.vendor_id.property_account_payable_id.id),
            'type': 'in_invoice',
            'invoice_line_ids': [line for line in lines]
        })

        for fuel in active_ids:
            fuel.write({'invoice_id': invoice_id.id})
