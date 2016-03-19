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

from openerp import models
import time
from openerp.tools.translate import _
import DEFAULT_SERVER_DATETIME_FORMAT


# Wizard que permite crear la factura de proveedor de la(s)
# cartas porte(s) seleccionadas
class TmsWaybillSupplierInvoice(models.TransientModel):

    """ To create Supplier invoice for each Waybill"""

    _name = 'tms.waybill.supplier_invoice'
    _description = 'Make Supplier Invoices from Waybill'

    def make_waybill_supplier_invoices(self):

        """
             To get Waybills and create Invoices
             @param self: The object pointer.
             @param cr: A database cursor
             @param uid: ID of the user currently logged in
             @param context: A standard dictionary
             @return : retrun view of Invoice
        """

        if self is None:
            record_ids = self
        else:
            record_ids = self.pool.get('active_ids', [])

        if record_ids:
            # res = False
            invoices = []
            # factor = self.pool.get('tms.factor')
            # property_obj = self.pool.get('ir.property')
            # partner_obj = self.pool.get('res.partner')
            fpos_obj = self.pool.get('account.fiscal.position')
            prod_obj = self.pool.get('product.product')
            account_jrnl_obj = self.pool.get('account.journal')
            invoice_obj = self.pool.get('account.invoice')
            waybill_obj = self.pool.get('tms.waybill')
            travel_obj = self.pool.get('tms.travel')

            journal_id = account_jrnl_obj.search(
                [('type', '=', 'purchase'),
                 ('tms_supplier_journal', '=', 1)], context=None)
            if not journal_id:
                raise Warning(
                    'Error !',
                    _('You have not defined TMS Supplier Purchase Journal...'))
            journal_id = journal_id and journal_id[0]
            prod_id = prod_obj.search(
                [('tms_category', '=', 'freight'),
                 ('tms_default_supplier_freight', '=', 1),
                 ('active', '=', 1)], limit=1)
            if not prod_id:
                raise Warning(
                    _('Missing configuration !'),
                    _('There is no product defined as Freight !!!'))
            product = prod_obj.browse(prod_id, context=None)[0]
            # print "product.name : ", product.name
            prod_account = product.product_tmpl_id.property_account_expense.id
            if not prod_account:
                prod_account = (product.categ_id.
                                property_account_expense_categ.id)
                if not prod_account:
                    raise Warning(
                        ('Error !'),
                        _('There is no expense account defined for this \
                        product: "%s" (id:%d)') % (product.name, product.id,))

            prod_account = fpos_obj.map_account(False, prod_account)

            self.execute("select distinct supplier_id, currency_id from \
                tms_waybill where waybill_type='outsourced' and \
                supplier_invoice_id is null and (state='confirmed' or \
                (state='approved' and billing_policy='automatic')) and id \
                IN %s", (tuple(record_ids),))
            data_ids = self.fetchall()
            if not len(data_ids):
                raise Warning(
                    _('Warning !'),
                    _('Not all selected records are Confirmed yet or already \
                    invoiced or selected records are not from Outsourced \
                    Freights...'))
            # print data_ids

            for data in data_ids:
                # partner = partner_obj.browse(data[0])
                self.execute("select id from tms_waybill where \
                    waybill_type='outsourced' and supplier_invoice_id is \
                    null and (state='confirmed' or (state='approved' and \
                    billing_policy='automatic')) and supplier_id=\
                " + str(data[0]) + ' and currency_id=' + str(data[1]) + " \
                and id IN %s", (tuple(record_ids),))
                waybill_ids = filter(None, map(
                    lambda x: x[0], self.fetchall()))

                notes = "Cartas Porte"
                # inv_amount = 0.0
                # empl_name = ''

                inv_lines = []
                for waybill in waybill_obj.browse(waybill_ids):
                    # currency_id = waybill.currency_id.id

                    inv_line = (0, 0, {
                        'name': (
                            product.name + ' - Viaje: ' +
                            (waybill.travel_id.name or _('Sin Viaje')) +
                            ' - ' + _('Waybill: ') + waybill.name),
                        'origin': waybill.name,
                        'account_id': prod_account,
                        'price_unit': waybill.supplier_amount,
                        'quantity': 1.0,
                        'uos_id': product.uom_id.id,
                        'product_id': product.id,
                        'invoice_line_tax_id': [
                            (6, 0,
                             [x.id for x in product.supplier_taxes_id])],
                        'note': (
                            'Carta Porte de Permisionario ' +
                            (waybill.travel_id.name or _('Sin Viaje'))),
                        'account_analytic_id': False,
                    })
                    inv_lines.append(inv_line)
                    notes += '\n' + waybill.name
                    departure_address_id = waybill.departure_address_id.id
                    arrival_address_id = waybill.arrival_address_id.id

                    a = waybill.supplier_id.property_account_payable.id
                    if not a:
                        raise Warning(
                            _('Warning !'),
                            _('Supplier << %s >> has not Payable Account \
                                defined.') % (waybill.supplier_id.name))

                    if (waybill.supplier_id.id and
                            waybill.supplier_id.
                            property_supplier_payment_term.id):
                        pay_term = (waybill.supplier_id.
                                    property_supplier_payment_term.id)
                    else:
                        pay_term = False

                inv = {
                    'name': 'Fletes de Permisionario',
                    'origin': waybill.name,
                    'type': 'in_invoice',
                    'journal_id': journal_id,
                    'reference': 'Factura de Cartas Porte de Permisionario',
                    'account_id': a,
                    'partner_id': waybill.supplier_id.id,
                    'departure_address_id': departure_address_id,
                    'arrival_address_id': arrival_address_id,
                    'address_invoice_id':
                        self.pool.get('res.partner').address_get(
                            [waybill.supplier_id.id], ['default'])['default'],
                    'address_contact_id':
                        self.pool.get('res.partner').address_get(
                            [waybill.supplier_id.id], ['default'])['default'],
                    'invoice_line': [x for x in inv_lines],
                    'comment': 'Factura de Cartas Porte de Permisionario',
                    'payment_term': pay_term,
                    'fiscal_position':
                        waybill.supplier_id.property_account_position.id,
                    'comment': notes,
                    'tms_type': (
                        'invoice' if waybill.billing_policy == 'manual'
                        else 'waybill')
                }
                # print "inv: " , inv

                travel_obj.write(
                    [waybill.travel_id.id],
                    {'closed_by': self,
                     'date_closed':
                     time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                     'state': 'closed'})

                inv_id = invoice_obj.create(inv)
                invoices.append(inv_id)

                waybill_obj.write(
                    waybill_ids,
                    {'supplier_invoice_id': inv_id,
                     'supplier_invoiced_by': self,
                     'supplier_invoiced_date':
                     time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)})

            ir_model_data = self.pool.get('ir.model.data')
            act_obj = self.pool.get('ir.actions.act_window')
            result = ir_model_data.get_object_reference(
                'account', 'action_invoice_tree2')
            id = result and result[1] or False
            result = act_obj.read([id])[0]
            result['domain'] = ("[('id','in', [" +
                                ','.join(map(str, invoices)) + "])]")
            return result
