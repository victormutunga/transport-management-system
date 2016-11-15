# -*- coding: utf-8 -*-
# © <2012> <Israel Cruz Argil, Argil Consulting>
# © <2016> <Jarsa Sistemas, S.A. de C.V.>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp import _, api, exceptions, models


class TmsWaybillInvoice(models.TransientModel):

    """ To create payment for Waybill"""

    _name = 'tms.waybill.invoice'
    _description = 'Make Payment for Advances'

    @api.multi
    def make_waybill_invoices(self):
        active_ids = self.env['tms.waybill'].browse(
            self._context.get('active_ids'))
        if not active_ids:
            return {}

        partner_ids = []
        total = 0.0
        waybill_names = ''
        control = 0
        lines = []
        for waybill in active_ids:
            if len(waybill.invoice_id) > 0:
                raise exceptions.ValidationError(
                    _('The waybill already has an invoice'))
            else:
                if (waybill.state in ('confirmed', 'closed') and not
                        waybill.invoice_paid):
                    partner_address = waybill.partner_invoice_id.address_get(
                        ['invoice', 'contact']).get('invoice', False)
                    if not partner_address:
                        raise exceptions.ValidationError(
                            _('You must configure the home address for the'
                              ' Customer.'))
                    partner_ids.append(partner_address)
                    currency = waybill.currency_id
                    total += currency.compute(waybill.amount_total,
                                              self.env.user.currency_id)
                    waybill_names += ' ' + waybill.name + ', '
                else:
                    raise exceptions.ValidationError(
                        _('The waybills must be in confirmed / closed state'
                          ' and unpaid.'))
                for product in waybill.waybill_line_ids:
                    if product.price_subtotal > 0.0:
                        lines.append(
                            (0, 0, {
                                'product_id': product.product_id.id,
                                'quantity': product.product_qty,
                                'price_unit': product.price_subtotal,
                                'invoice_line_tax_ids': [(
                                    6, 0,
                                    [x.id for x in product.tax_ids]
                                )],
                                'name': product.name,
                                'account_id': product.account_id.id,
                            }))
        for partner_id in partner_ids:
            if control == 0:
                old_partner = partner_id
                current_partner = partner_id
                control = 1
            else:
                current_partner = partner_id
            if old_partner != current_partner:
                raise exceptions.ValidationError(
                    _('The waybills must be of the same customer. '
                      'Please check it.'))
            else:
                old_partner = partner_id

        invoice_id = self.env['account.invoice'].create({
            'partner_id': waybill.partner_id.id,
            'fiscal_position_id': (
                waybill.partner_id.property_account_position_id.id),
            'reference': waybill_names,
            'currency_id': currency.id,
            'account_id': (
                waybill.partner_id.property_account_payable_id.id),
            'type': 'out_invoice',
            'invoice_line_ids': [line for line in lines],
        })

        for waybill in active_ids:
            waybill.write({'invoice_id': invoice_id.id})
