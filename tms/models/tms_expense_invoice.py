
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
from openerp import netsvc
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT

# Wizard que permite generar la poliza con el monto a pagar correspondiente a
# la liquidación del Operador


class TmsExpenseInvoice(models.TransientModel):

    """ To create invoice for each Expense"""

    _name = 'tms.expense.invoice'
    _description = 'Make Invoices from Expense Records'

    def make_invoices(self, ids, context=None):
        """
             To get Expense Record and create Invoice
             @param self: The object pointer.
             @param cr: A database cursor
             @param uid: ID of the user currently logged in
             @param context: A standard dictionary
             @return : retrun view of Invoice
        """

        if context is None:
            record_ids = ids
        else:
            record_ids = self.pool.get('active_ids', [])
        if record_ids:
            res = False
            # invoices = []
            # property_obj = self.pool.get('ir.property')
            # partner_obj = self.pool.get('res.partner')
            # user_obj = self.pool.get('res.users')
            account_fiscal_obj = self.pool.get('account.fiscal.position')
            account_jrnl_obj = self.pool.get('account.journal')
            # invoice_obj = self.pool.get('account.invoice')
            expense_obj = self.pool.get('tms.expense')
            expense_line_obj = self.pool.get('tms.expense.line')
            period_obj = self.pool.get('account.period')
            move_obj = self.pool.get('account.move')
            journal_id = account_jrnl_obj.search(
                [('type', '=', 'general'),
                 ('tms_expense_journal', '=', 1)],
                context=None)
            if not journal_id:
                raise Warning(
                    'Error !',
                    'You have not defined Travel Expense Purchase Journal...')
            journal_id = journal_id and journal_id[0]
            self.execute("select distinct employee_id, currency_id from \
                tms_expense where invoice_id is null and state='approved' and \
                id IN %s", (tuple(record_ids),))
            data_ids = self.fetchall()
            if not len(data_ids):
                raise Warning(
                    'Warning !',
                    'Selected records are not Approved or already sent for \
                    payment...')
            for data in data_ids:
                expenses_ids = expense_obj.search(
                    [('state', '=', 'approved'),
                     ('employee_id', '=', data[0]),
                     ('currency_id', '=', data[1]),
                     ('id', 'in', tuple(record_ids),)])
                for expense in expense_obj.browse(expenses_ids):
                    period_id = period_obj.search(
                        [('date_start', '<=', expense.date),
                         ('date_stop', '>=', expense.date),
                         ('state', '=', 'draft')], context=None)
                    if not period_id:
                        raise Warning(
                            _('Warning !'),
                            _('There is no valid account period for this \
                                date %s. Period does not exists or is already \
                                closed') % (expense.date,))
                    if not (expense.employee_id.tms_advance_account_id.id and
                            expense.employee_id.tms_expense_negative_balance_account_id.id):
                        raise Warning(
                            _('Warning !'),
                            _('There is no advance account and/or Travel \
                                Expense Negative Balance account defined for \
                                this driver: "%s" (id:%d)') % (
                                expense.employee_id.name,
                                expense.employee_id.id,))
                    if not (expense.employee_id.address_home_id and
                            expense.employee_id.address_home_id.id):
                        raise Warning(
                            _('Warning !'),
                            _('There is no Address defined for this \
                                driver: "%s" (id:%d)') % (
                                expense.employee_id.name,
                                expense.employee_id.id,))
                    advance_account = expense.employee_id.tms_advance_account_id.id
                    negative_balance_account = expense.employee_id.tms_expense_negative_balance_account_id.id
                    advance_account = account_fiscal_obj.map_account(
                        False, advance_account)
                    negative_balance_account = account_fiscal_obj.map_account(
                        False, negative_balance_account)

                    move_lines = []
                    precision = self.pool.get(
                        'decimal.precision').precision_get('Account')
                    notes = _("Travel Expense Record ")
                    # Revisamos si tiene Anticipos de Viaje para descontarlo
                    # del saldo del Operador
                    if expense.amount_advance:
                        move_line = (0, 0, {
                            'name': _('Advance Discount'),
                            'account_id': advance_account,
                            'debit': 0.0,
                            'credit': round(expense.amount_advance, precision),
                            'journal_id': journal_id,
                            'period_id': period_id[0],
                            'vehicle_id': expense.unit_id.id,
                            'employee_id': expense.employee_id.id,
                            'sale_shop_id': expense.shop_id.id,
                            'partner_id':
                            expense.employee_id.address_home_id.id,
                        })
                        move_lines.append(move_line)
                        notes += '\n' + _('Advance Discount')

                    # ## Recorremos las lineas de gastos, estas deben ser
                    # cualquiera excepto:
                    # ## * Vales de Combustible
                    # ## * Facilidades administrativas

                    invoice_ids = []
                    for line in expense.expense_line:
                        if (line.line_type != ('madeup_expense') and not
                                line.fuel_voucher):
                            prod_account = (
                                negative_balance_account
                                if line.product_id.tms_category == 'negative_balance'
                                else line.product_id.property_account_expense.id
                                if line.product_id.property_account_expense.id
                                else line.product_id.categ_id.property_account_expense_categ.id
                                if line.product_id.categ_id.property_account_expense_categ.id
                                else False)
                            if not prod_account:
                                raise Warning(
                                    _('Warning !'),
                                    _('Expense Account is not defined for \
                                        product %s (id:%d)') % (
                                        line.product_id.name,
                                        line.product_id.id,))
                            inv_id = False
                            if line.is_invoice:
                                inv_id = self.create_supplier_invoice(line)
                                invoice_ids.append(inv_id)
                                yres = expense_line_obj.write(
                                    [line.id], {'invoice_id': inv_id})
                            # ## Creamos la partida de cada Gasto "Valido"
                            move_line = (0, 0, {
                                'name': (expense.name + ((' |%s|' % (inv_id))
                                         if inv_id else '') + line.name),
                                'ref': (expense.name + ' - Inv ID - ' +
                                        str(inv_id) if inv_id else ''),
                                'product_id': line.product_id.id,
                                'product_uom_id': line.product_uom.id,
                                'account_id':
                                (account_fiscal_obj.map_account(
                                    False, prod_account)
                                 if not line.is_invoice
                                 else
                                 line.partner_id.property_account_payable.id),
                                'debit': ((round(line.price_subtotal,
                                                 precision)
                                          if line.price_subtotal > 0.0
                                          else 0.0)
                                          if not line.is_invoice
                                          else (line.price_total +
                                                (line.special_tax_amount or
                                                    0.0))),
                                'credit':
                                (round(abs(line.price_subtotal), precision)
                                    if line.price_subtotal <= 0.0 else 0.0),
                                'quantity': line.product_uom_qty,
                                'journal_id': journal_id,
                                'period_id': period_id[0],
                                'vehicle_id': expense.unit_id.id,
                                'employee_id': expense.employee_id.id,
                                'sale_shop_id': expense.shop_id.id,
                                'partner_id':
                                (expense.employee_id.address_home_id.id
                                    if not line.is_invoice
                                    else line.partner_id.id),
                            })
                            move_lines.append(move_line)
                            notes += '\n' + line.name
                            # ## En caso de que el producto tenga definido
                            # impuestos, generamos las partidas
                            # correspondientes.
                            for tax in line.product_id.supplier_taxes_id:
                                tax_account = tax.account_collected_voucher_id.id
                                if not tax_account:
                                    raise Warning(
                                        _('Warning !'),
                                        _('Tax Account is not defined for \
                                        Tax %s (id:%d)') % (tax.name, tax.id,))
                                tax_amount = round(line.price_subtotal *
                                                   tax.amount, precision)

                                move_line = (0, 0, {
                                    'name': (
                                        expense.name + ' - ' +
                                        tax.name + ' - ' +
                                        line.name + ' - ' +
                                        line.employee_id.name + ' (' +
                                        str(line.employee_id.id) + ')'),
                                    'ref': expense.name,
                                    'account_id':
                                    account_fiscal_obj.map_account(
                                        False, tax_account),
                                    'debit':
                                    (round(tax_amount, precision)
                                        if tax_amount > 0.0 else 0.0),
                                    'credit':
                                    (round(abs(tax_amount), precision)
                                        if tax_amount <= 0.0 else 0.0),
                                    'journal_id': journal_id,
                                    'period_id': period_id[0],
                                    'tax_id_secondary': (
                                        tax.id if line.is_invoice else False),
                                    'amount_base':
                                    (round(abs(line.price_subtotal), precision)
                                        if line.is_invoice else False),
                                })
                                move_lines.append(move_line)
                                # ## En caso de que sea una factura, se genera
                                # automaticamente la cancelación del impuesto
                                if line.is_invoice:
                                    tax_account = tax.account_collected_id.id
                                    if not tax_account:
                                        raise Warning(
                                            _('Warning !'),
                                            _('Tax Account is not defined for \
                                                Tax %s (id:%d)') % (
                                                tax.name, tax.id,))
                                    tax_amount = round(line.price_subtotal *
                                                       tax.amount, precision)
                                    move_line = (0, 0, {
                                        'name': (
                                            expense.name + ' - ' +
                                            tax.name + ' - ' +
                                            line.name + ' - ' +
                                            line.employee_id.name + ' (' +
                                            str(line.employee_id.id) + ')'),
                                        'ref': expense.name,
                                        'account_id':
                                        account_fiscal_obj.map_account(
                                            False, tax_account),
                                        'debit':
                                        (round(tax_amount, precision)
                                            if tax_amount <= 0.0 else 0.0),
                                        'credit':
                                        (round(abs(tax_amount), precision)
                                            if tax_amount > 0.0 else 0.0),
                                        'journal_id': journal_id,
                                        'period_id': period_id[0],
                                        # 'tax_id_secondary' : tax.id,
                                        # 'amount_base'   :
                                        # round(abs(line.price_subtotal),precision),
                                    })
                                    move_lines.append(move_line)
                    if expense.amount_balance < 0:
                        move_line = (0, 0, {
                            'name': _('Negative Balance'),
                            'ref': expense.name,
                            'account_id': negative_balance_account,
                            'debit':
                            round(expense.amount_balance * -1.0, precision),
                            'credit': 0.0,
                            'journal_id': journal_id,
                            'period_id': period_id[0],
                            'vehicle_id': expense.unit_id.id,
                            'employee_id': expense.employee_id.id,
                            'partner_id':
                            expense.employee_id.address_home_id.id,
                        })
                        notes += '\n' + _('Debit Balance')
                    else:
                        b = line.employee_id.address_home_id.property_account_payable.id
                        if not b:
                            raise Warning(
                                _('Warning !'),
                                _('There is no address created for this \
                                    driver or there is no payable account \
                                    defined for: "%s" (id:%d)') % (
                                    line.employee_id.name,
                                    line.employee_id.id,))
                        b = account_fiscal_obj.map_account(False, b)
                        move_line = (0, 0, {
                            'name': _('Positive Balance'),
                            'ref': expense.name,
                            'account_id': b,
                            'debit': 0.0,
                            'credit': round(expense.amount_balance, precision),
                            'journal_id': journal_id,
                            'period_id': period_id[0],
                            'vehicle_id': expense.unit_id.id,
                            'employee_id': expense.employee_id.id,
                            'partner_id':
                            expense.employee_id.address_home_id.id,
                        })
                        notes += '\n' + _('Credit Balance')
                    move_lines.append(move_line)
                    move = {
                        'ref': expense.name,
                        'journal_id': journal_id,
                        'narration':
                        (_('TMS-Travel Expense Record') + ' - ' +
                            expense.name + ' - ' +
                            expense.employee_id.name + ' (' +
                            str(expense.employee_id.id) + ')'),
                        'line_id': [x for x in move_lines],
                        'date': expense.date,
                        'period_id': period_id[0],
                    }
                    move_id = move_obj.create(move)
                    if move_id:
                        move_obj.button_validate([move_id])
                    expense_obj.write(
                        [expense.id],
                        {'move_id': move_id,
                         'state': 'confirmed',
                         'confirmed_by': self,
                         'date_confirmed':
                         time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)})
                    # res = self.reconcile_supplier_invoices(
                    #    move_id, invoice_ids)
        return True

    def reconcile_supplier_invoices(self, move_id, invoice_ids):
        if self is None:
            self = {}
        move_line_obj = self.pool.get('account.move.line')
        for invoice in self.pool.get('account.invoice').browse(invoice_ids):
            xid = '%s' % (invoice.id)
            res = move_line_obj.search(
                [('move_id', '=', move_id), ('name', 'ilike', xid)])
            if not res:
                raise Warning(
                    'Error !',
                    _('Move line was not found, please check your data...'))
            # print "invoice.id: ", invoice.id
            # print "invoice.number: ", invoice.number
            # print "invoice.supplier_invoice_number: ",
            #   invoice.supplier_invoice_number
            # print "invoice.amount_untaxed: ",  invoice.amount_untaxed
            # print "invoice.amount_tax: ", invoice.amount_tax
            # print "invoice.amount_total: ", invoice.amount_total
            # print "invoice.residual: ", invoice.residual
            # print "invoice.partner_id: (%s) %s" %
            #   (invoice.partner_id.id, invoice.partner_id.name)
            # for move_line in invoice.move_id.line_id:
            # if move_line.account_id.type == 'payable':
            # print "move_line.account_id %s - %s" %
            #   (move_line.account_id.code, move_line.account_id.name)
            # lines = res + [move_line.id]
            # for xline in move_line_obj.browse(cr, uid, lines):
            #    print "xline.account_id %s - %s" %
            #       (xline.account_id.code, xline.account_id.name)
            #    print "xline.debit: ", xline.debit
            #    print "xline.credit: ", xline.credit
            #    print "xline.partner_id: (%s) %s" %
            #       (xline.partner_id.id, xline.partner_id.name)
            #    print "xline.invoice.number: ",
            #       xline.invoice.number if xline.invoice else ''
            #    print "xline.invoice.supplier_invoice_number: ",
            #       xline.invoice.supplier_invoice_number if
            #       xline.invoice else ''
            #    print "xline.invoice.id: ", xline.invoice.id if
            #       xline.invoice else ''
            # res2 = move_line_obj.reconcile(lines, context=context)
        return

    def create_supplier_invoice(self, line):
        invoice_obj = self.pool.get('account.invoice')
        invoice_tax_obj = self.pool.get('account.invoice.tax')
        expense_line_obj = self.pool.get('tms.expense.line')
        journal_id = self.pool.get('account.journal').search(
            [('type', '=', 'purchase'),
             ('tms_expense_suppliers_journal', '=', 1)])
        if not journal_id:
            raise Warning(
                'Error !',
                _('You have not defined Travel Expense Supplier Journal...'))
        journal_id = journal_id and journal_id[0]

        if line.product_id:
            a = line.product_id.product_tmpl_id.property_account_expense.id
            if not a:
                a = line.product_id.categ_id.property_account_expense_categ.id
            if not a:
                raise Warning(
                    _('Error !'),
                    _('There is no expense account defined for this \
                        product: "%s" (id:%d)') % (line.product_id.name,
                                                   line.product_id.id,))
        else:
            a = property_obj.get(
                'property_account_expense_categ', 'product.category').id
        account_fiscal_obj = self.pool.get('account.fiscal.position')
        a = account_fiscal_obj.map_account(cr, uid, False, a)
        inv_line = (0, 0, {
            'name': _('%s (TMS Expense Record %s)') % (line.product_id.name,
                                                       line.expense_id.name),
            'origin': line.expense_id.name,
            'account_id': a,
            'quantity': line.product_uom_qty,
            'price_unit': line.price_unit,
            'invoice_line_tax_id':
            [(6, 0,
                [x.id for x in line.product_id.supplier_taxes_id])],
            'uos_id': line.product_uom.id,
            'product_id': line.product_id.id,
            'notes': line.name,
            'account_analytic_id': False,
            'vehicle_id': line.expense_id.unit_id.id,
            'employee_id': line.expense_id.employee_id.id,
            'sale_shop_id': line.expense_id.shop_id.id,
        })
        # print "Subtotal Factura: ", round(line.price_subtotal /
        #     line.product_uom_qty, 4)
        notes = line.expense_id.name + ' - ' + line.product_id.name
        a = line.partner_id.property_account_payable.id
        inv = {
            'supplier_invoice_number': line.invoice_number,
            'name': line.expense_id.name + ' - ' + line.invoice_number,
            'origin': line.expense_id.name,
            'type': 'in_invoice',
            'journal_id': journal_id,
            'reference': line.expense_id.name + ' - ' + line.invoice_number,
            'account_id': a,
            'partner_id': line.partner_id.id,
            'invoice_line': [inv_line],
            'currency_id': line.expense_id.currency_id.id,
            'comment': line.expense_id.name + ' - ' + line.invoice_number,
            'payment_term': (
                line.partner_id.property_payment_term and
                line.partner_id.property_payment_term.id or False),
            'fiscal_position':
            line.partner_id.property_account_position.id or False,
            'comment': notes,
        }

        inv_id = invoice_obj.create(cr, uid, inv)
        if line.special_tax_amount:
            invoice_obj.button_reset_taxes(cr, uid, [inv_id])
            for tax_line in invoice_obj.browse(cr, uid, inv_id).tax_line:
                if tax_line.amount == 0.0:
                    invoice_tax_obj.write(
                        [tax_line.id], {'amount': line.special_tax_amount})
        wf_service = netsvc.LocalService('workflow')
        wf_service.trg_validate(uid, 'account.invoice', inv_id, 'invoice_open')
        res = expense_line_obj.write([line.id], {'invoice_id': inv_id})
        return inv_id
