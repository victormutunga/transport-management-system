# -*- coding: utf-8 -*-
# © <2012> <Israel Cruz Argil, Argil Consulting>
# © <2016> <Jarsa Sistemas, S.A. de C.V.>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import time

from openerp import fields, models
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.tools.translate import _


class TmsWaybillInvoice(models.TransientModel):

    """ To create invoice for each Waybill"""

    _name = 'tms.waybill.invoice'
    _description = 'Make Invoices from Waybill'

    group_line_product = fields.Boolean(
        'Group Waybill Lines',
        help='Group Waybill Lines Quantity & Subtotal by Product',
        default=True)

    def make_waybill_invoices(self, ids, context=None):

        """
             To get Waybills and create Invoices
             @param self: The object pointer.
             @param cr: A database cursor
             @param uid: ID of the user currently logged in
             @param context: A standard dictionary
             @return : retrun view of Invoice
        """

        if context is None:
            record_ids = ids
        else:
            record_ids = context.get('active_ids', [])

        group_lines = self.browse(self)[0].group_line_product

        if record_ids:
            # res = False
            invoices = []
            # shipped_grouped_obj=self.pool.get('tms.waybill.shipped_grouped')
            property_obj = self.pool.get('ir.property')
            partner_obj = self.pool.get('res.partner')
            # user_obj = self.pool.get('res.users')
            account_fiscal_obj = self.pool.get('account.fiscal.position')
            # invoice_line_obj = self.pool.get('account.invoice.line')
            account_jrnl_obj = self.pool.get('account.journal')
            invoice_obj = self.pool.get('account.invoice')
            waybill_obj = self.pool.get('tms.waybill')

            journal_id = account_jrnl_obj.search(
                [('type', '=', 'sale')], context=None)
            journal_id = journal_id and journal_id[0] or False

            self.execute("select distinct partner_id, currency_id from \
                tms_waybill where (invoice_id is null or \
                (select account_invoice.state from account_invoice \
                where account_invoice.id = \
                tms_waybill.invoice_id)='cancel') and \
                (state='confirmed' or (state='approved' and \
                billing_policy='automatic')) and id IN %s\
                ", (tuple(record_ids),))
            data_ids = self.fetchall()
            if not len(data_ids):
                raise Warning(
                    _('Warning !'),
                    _('Not all selected records are Confirmed yet or already \
                        invoiced...'))
            # print data_ids

            for data in data_ids:
                if not data[0]:
                    raise Warning(
                        _('Warning !'),
                        _('You have not defined Client account...'))
                partner = partner_obj.browse(data[0])
                self.execute("select id from tms_waybill where (invoice_id is \
                    null or (select account_invoice.state from \
                    account_invoice where account_invoice.id = \
                    tms_waybill.invoice_id)='cancel') and \
                    (state='confirmed' or (state='approved' and \
                    billing_policy='automatic')) and partner_id=\
                " + str(data[0]) + ' and currency_id=' + str(data[1]) +
                    " and id IN %s", (tuple(record_ids),))
                waybill_ids = filter(
                    None, map(lambda x: x[0], self.fetchall()))
                # print "waybill_ids : ", waybill_ids
                inv_lines = []
                notes = _("Waybills")
                # inv_amount = 0.0
                # empl_name = ''
                product_shipped_grouped = {}
                for waybill in waybill_obj.browse(waybill_ids):
                    fpos = (waybill.partner_id.property_account_position.id or
                            False)
                    fpos = fpos and account_fiscal_obj.browse(fpos) or False

                    for shipped_prod in waybill.waybill_shipped_product:
                        # *****************************************
                        val = {
                            'product_name': shipped_prod.product_id.name,
                            'product_id': shipped_prod.product_id.id,
                            'product_uom': shipped_prod.product_uom.id,
                            'quantity': shipped_prod.product_uom_qty,
                        }
                        key = (val['product_id'], val['product_uom'],
                               val['product_name'])
                        if key not in product_shipped_grouped:
                            product_shipped_grouped[key] = val
                        else:
                            product_shipped_grouped[key]['quantity'] += val[
                                'quantity']
                        # *****

                    # currency_id = waybill.currency_id.id
                    for line in waybill.waybill_line:
                        if line.line_type == 'product':
                            if line.product_id:
                                a = (line.product_id.product_tmpl_id.
                                     property_account_income.id)
                                if not a:
                                    a = (line.product_id.categ_id.
                                         property_account_income_categ.id)
                                if not a:
                                    a = property_obj.get(
                                        'property_account_income_categ',
                                        'product.category',
                                        context=context).id
                                if not a:
                                    raise Warning(
                                        _('Error !'),
                                        _('There is no income account defined \
                                        for this product: "%s" (id:%d)\
                                        ') % (line.product_id.name,
                                              line.product_id.id,))

                                a = account_fiscal_obj.map_account(False, a)

                                inv_line = (0, 0, {
                                    'name': line.name,
                                    'origin': line.waybill_id.name,
                                    'account_id': a,
                                    'price_unit': line.price_unit,
                                    'quantity': line.product_uom_qty,
                                    'uos_id': line.product_uom.id,
                                    'product_id': line.product_id.id,
                                    'invoice_line_tax_id': [
                                        (6, 0,
                                         [_w for _w in
                                          account_fiscal_obj.map_tax(
                                            fpos, line.product_id.taxes_id)])],
                                    'vehicle_id': (
                                        line.waybill_id.travel_id.unit_id.id if
                                        line.waybill_id.travel_id else False),
                                    'employee_id': (
                                        (line.waybill_id.travel_id.
                                         employee_id.id) if
                                        line.waybill_id.travel_id else False),
                                    'sale_shop_id': line.waybill_id.shop_id.id,
                                    'note': line.notes,
                                    # 'account_analytic_id': False,
                                })
                                inv_lines.append(inv_line)
                        notes += ', ' + line.waybill_id.name
                    # *****
                    # print "inv_lines: ", inv_lines
                    if group_lines:
                        # print "Si entra a agrupar lineas de Cartas Porte"
                        line_grouped = {}
                        for xline in inv_lines:
                            val = {
                                'name': xline[2]['name'],
                                'origin': xline[2]['origin'],
                                'account_id': xline[2]['account_id'],
                                'price_unit': xline[2]['price_unit'],
                                'quantity': xline[2]['quantity'],
                                'uos_id': xline[2]['uos_id'],
                                'product_id': xline[2]['product_id'],
                                'invoice_line_tax_id':
                                    xline[2]['invoice_line_tax_id'],
                                'note': xline[2]['note'],
                                # 'vehicle_id': xline[2]['vehicle_id'],
                                # 'employee_id': xline[2]['employee_id'],
                                # 'sale_shop_id': xline[2]['sale_shop_id'],
                            }
                            # print "val: ", val
                            key = (val['product_id'], val['uos_id'])
                            # , val['vehicle_id'], val['employee_id'],
                            #   val['sale_shop_id'])
                            # print "key: ", key
                            if key not in line_grouped:
                                line_grouped[key] = val
                            else:
                                line_grouped[key][
                                    'price_unit'] += val['price_unit']

                        # print "line_grouped: ", line_grouped
                        inv_lines = []
                        for t in line_grouped.values():
                            # print "t: ", t
                            vals = (0, 0, {
                                    'name': t['name'],
                                    'origin': t['origin'],
                                    'account_id': t['account_id'],
                                    'price_unit': t['price_unit'],
                                    'quantity': t['quantity'],
                                    'uos_id': t['uos_id'],
                                    'product_id': t['product_id'],
                                    'invoice_line_tax_id':
                                        t['invoice_line_tax_id'],
                                    'note': t['note'],
                                    # 'vehicle_id'    : t['vehicle_id'],
                                    # 'employee_id'   : t['employee_id'],
                                    # 'sale_shop_id'  : t['sale_shop_id'],
                                    })
                            inv_lines.append(vals)
                        # print "inv_lines: ", inv_lines
                # ******
                    departure_address_id = waybill.departure_address_id.id
                    arrival_address_id = waybill.arrival_address_id.id
                a = partner.property_account_receivable.id
                if partner and partner.property_payment_term.id:
                    pay_term = partner.property_payment_term.id
                else:
                    pay_term = False

                inv = {
                    'name': 'Factura',
                    'origin': 'Fact. de Cartas Porte',
                    'type': 'out_invoice',
                    'journal_id': journal_id,
                    'reference': 'Fact. de Cartas Porte',
                    'account_id': a,
                    'partner_id': waybill.partner_id.id,
                    'departure_address_id': departure_address_id,
                    'arrival_address_id': arrival_address_id,
                    'address_invoice_id':
                        self.pool.get('res.partner').address_get(
                            [partner.id], ['default'])['default'],
                    'address_contact_id':
                        self.pool.get('res.partner').address_get(
                            [partner.id], ['default'])['default'],
                    'invoice_line': [x for x in inv_lines],
                    'comment': 'Fact. de Cartas Porte' + notes,
                    'payment_term': pay_term,
                    'fiscal_position': partner.property_account_position.id,
                    'pay_method_id': partner.pay_method_id.id,
                    'acc_payment': (
                        partner.bank_ids[0].id if
                        partner.bank_ids and
                        partner.bank_ids[0] else False),
                    'tms_type': (
                        'invoice' if waybill.billing_policy ==
                        'manual' else 'waybill')
                }

                inv_id = invoice_obj.create(inv)
                invoices.append(inv_id)
                # ******
                # print "product_shipped_grouped: ", product_shipped_grouped
                for t in product_shipped_grouped.values():
                    # print "t: ", t
                    vals = {
                        'invoice_id': inv_id,
                        'product_id': t['product_id'],
                        'product_uom': t['product_uom'],
                        'quantity': t['quantity'],
                    }
                    # res = shipped_grouped_obj.create(cr, uid, vals)
                # ******
                waybill_obj.write(waybill_ids, {
                    'invoice_id': inv_id,
                    'state': 'confirmed',
                    'confirmed_by': self,
                    'date_confirmed':
                    time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)})
            ir_model_data = self.pool.get('ir.model.data')
            act_obj = self.pool.get('ir.actions.act_window')
            result = ir_model_data.get_object_reference(
                'account', 'action_invoice_tree1')
            id = result and result[1] or False
            result = act_obj.read([id], context=context)[0]
            result['domain'] = "[('id','in', [" + ','.join(map(
                str, invoices)) + "])]"
            return result
