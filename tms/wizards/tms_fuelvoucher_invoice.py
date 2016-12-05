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
        currency_ids = []
        control = 0
        control_c = 0
        fuel_names = []
        lines = []
        for fuel in active_ids:
            if len(fuel.invoice_id) > 0:
                raise exceptions.ValidationError(
                    _('The fuel already has an invoice'))
            else:
                if (fuel.state in ('confirmed', 'closed') and not
                        fuel.invoice_id):
                    partner_address = fuel.vendor_id.address_get(
                        ['invoice', 'contact']).get('invoice', False)
                    if not partner_address:
                        raise exceptions.ValidationError(
                            _('You must configure the invoice address for the'
                              ' Customer.'))
                    partner_ids.append(partner_address)
                    currency_ids.append(fuel.currency_id.id)

                else:
                    raise exceptions.ValidationError(
                        _('The fuels must be in confirmed / closed state'
                          ' and unpaid.'))
                fuel_names.append(fuel.name)

                product = fuel.product_id
                ieps = fuel.operating_unit_id.ieps_product_id
                if (product.property_account_expense_id and
                        ieps.property_account_expense_id):
                    account = product.property_account_expense_id
                    account_ieps = ieps.property_account_expense_id
                elif (product.categ_id.property_account_expense_categ_id and
                        ieps.categ_id.property_account_expense_categ_id):
                    account = (
                        product.categ_id.property_account_expense_categ_id)
                    account_ieps = (
                        ieps.categ_id.property_account_expense_categ_id)
                else:
                    raise exceptions.ValidationError(
                        _('You must have an expense account in the '
                          'product or its category'))

                fpos = fuel.vendor_id.property_account_position_id
                fpos_tax_ids = fpos.map_tax(fuel.product_id.supplier_taxes_id)
                lines.append(
                    (0, 0, {
                        'product_id': (
                            fuel.product_id.id),
                        'quantity': fuel.product_qty,
                        'price_unit': fuel.price_unit,
                        'invoice_line_tax_ids': [(
                            6, 0,
                            [x.id for x in fpos_tax_ids]
                        )],
                        'name': fuel.product_id.name,
                        'account_id': account.id}))

                lines.append((0, 0, {
                    'product_id': (
                        fuel.operating_unit_id.ieps_product_id.id),
                    'quantity': 1.0,
                    'price_unit': fuel.special_tax_amount,
                    'name': fuel.operating_unit_id.ieps_product_id.name,
                    'account_id': account_ieps.id})
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

        for currency in currency_ids:
            if control_c == 0:
                old_curerncy = currency
                current_curerncy = currency
                control_c = 1
            else:
                current_curerncy = currency
            if old_curerncy != current_curerncy:
                raise exceptions.ValidationError(
                    _('The fuels must be of the same currency. '
                      'Please check it.'))
            else:
                old_curerncy = currency
        if not fuel.vendor_id.property_account_payable_id:
            raise exceptions.ValidationError(
                _('Set account payable by vendor'))

        invoice_id = self.env['account.invoice'].create({
            'partner_id': fuel.vendor_id.id,
            'fiscal_position_id': fpos.id,
            'reference': "Invoice of: " + ', '.join(fuel_names),
            'journal_id': fuel.operating_unit_id.purchase_journal_id.id,
            'currency_id': fuel.currency_id.id,
            'account_id': (
                fuel.vendor_id.property_account_payable_id.id),
            'type': 'in_invoice',
            'invoice_line_ids': [line for line in lines]
        })

        for fuel in active_ids:
            fuel.write({'invoice_id': invoice_id.id})
        return {
            'name': 'Customer Invoice',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'current',
            'res_model': 'account.invoice',
            'res_id': invoice_id.id,
            'type': 'ir.actions.act_window'
        }
