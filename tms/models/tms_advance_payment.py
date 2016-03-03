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


from openerp.osv import osv, fields
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
import openerp.addons.decimal_precision as dp
import time


class tms_advance_payment(osv.osv_memory):

    """ To create payment for Advance"""

    _name = 'tms.advance.payment'
    _description = 'Make Payment for Advances'

    def makePayment(self, cr, uid, ids, context=None):

        if context is None:
            record_ids = ids
        else:
            record_ids =  context.get('active_ids',[])

        if not record_ids: return []
        ids = record_ids
        dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'account_voucher', 'view_vendor_receipt_dialog_form')
        cr.execute("select count(distinct(employee_id, currency_id)) from tms_advance where state in ('confirmed', 'closed') and not paid and id IN %s",(tuple(ids),))
        xids = filter(None, map(lambda x:x[0], cr.fetchall()))
        if len(xids) > 1:
            raise osv.except_osv('Error !',
                                 'You can not create Payment for several Driver Advances and or distinct currency...')
        amount = 0.0
        move_line_ids = []
        advance_names = ""
        for advance in self.pool.get('tms.advance').browse(cr, uid, ids, context=context):
            if advance.state in ('confirmed', 'closed') and not advance.paid:
                advance_names += ", " + advance.name
                amount += advance.total                
                for move_line in advance.move_id.line_id:
                    if move_line.credit > 0.0:
                        move_line_ids.append(move_line.id)
        if not amount:    
            raise osv.except_osv('Warning !',
                                 'All Driver Advances are already paid or are not in Confirmed State...')
        res = {
            'name':_("Driver Advance Payment"),
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'account.voucher',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]', 
            'context': {
                'payment_expected_currency': advance.currency_id.id,
                'default_partner_id': self.pool.get('res.partner')._find_accounting_partner(advance.employee_id.address_home_id).id,
                'default_amount': amount,
                'default_name': _('Driver Advance(s) %s') % (advance_names),
                'close_after_process': False,
                'move_line_ids': [x for x in move_line_ids],
                'default_type': 'payment',
                'type': 'payment'
            }}
        return res
