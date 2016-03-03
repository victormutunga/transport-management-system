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
import time
from openerp.tools.translate import _
from openerp import netsvc


# Wizard que permite hacer una copia de la carta porte al momento de cancelarla
class tms_waybill_cancel(osv.osv_memory):

    """ To create a copy of Waybill when cancelled"""

    _name = 'tms.waybill.cancel'
    _description = 'Make a copy of Cancelled Waybill'

    _columns = {
            'company_id'    : fields.many2one('res.company', 'Company'),
            'copy_waybill'  : fields.boolean('Create copy of this waybill?', required=False),
            'sequence_id'   : fields.many2one('ir.sequence', 'Sequence', required=False),
            'date_order'    : fields.date('Date', required=False),
        }

    _defaults = {'date_order'   : fields.date.context_today,
                 'company_id'   :  lambda self, cr, uid, context: self.pool.get('res.users').browse(cr, uid, uid).company_id.id
                 }

    def make_copy(self, cr, uid, ids, context=None):

        """
             To copy Waybills when cancelling them
             @param self: The object pointer.
             @param cr: A database cursor
             @param uid: ID of the user currently logged in
             @param context: A standard dictionary
             @return : retrun view of Invoice
        """

        record_id =  context.get('active_ids',[])

        #print record_id

        if record_id:
            #print "Si entra..."
            for record in self.browse(cr,uid, ids):
                #print record.company_id.name
                #print record.date_order
                waybill_obj = self.pool.get('tms.waybill')
                for waybill in waybill_obj.browse(cr, uid, record_id):
                    #print waybill.name
                    if waybill.invoiced and waybill.invoice_paid:
                        raise osv.except_osv(
                                _('Could not cancel Waybill !'),
                                _('This Waybill\'s Invoice is already paid'))
                        return False
                    elif waybill.invoiced and waybill.invoice_id and waybill.invoice_id.id and waybill.invoice_id.state != 'cancel' and waybill.billing_policy=='manual':
                        raise osv.except_osv(
                                _('Could not cancel Waybill !'),
                                _('This Waybill is already Invoiced'))
                        return False
                    elif waybill.waybill_type=='outsourced' and waybill.supplier_invoiced and waybill.supplier_invoice_paid:
                        raise osv.except_osv(
                                _('Could not cancel Waybill !'),
                                _('This Waybill\'s Supplier Invoice is already paid'))
                        return False

                    elif waybill.billing_policy=='automatic' and waybill.invoiced and not waybill.invoice_paid:
                        wf_service = netsvc.LocalService("workflow")
                        wf_service.trg_validate(uid, 'account.invoice', waybill.invoice_id.id, 'invoice_cancel', cr)
                        invoice_obj=self.pool.get('account.invoice')
                        invoice_obj.unlink(cr, uid, [waybill.invoice_id.id], context=None)
        #            elif waybill.state in ('draft','approved','confirmed') and waybill.travel_id.state in ('closed'):
        #                raise osv.except_osv(
        #                        _('Could not cancel Advance !'),
        #                        _('This Waybill is already linked to Travel Expenses record'))
                    #print "record_id:", record_id
                    elif waybill.waybill_type=='outsourced' and waybill.supplier_invoiced:
                        raise osv.except_osv(
                            _('Could not cancel Waybill !'),
                            _('This Waybill\'s Supplier Invoice is already created. First, cancel Supplier Invoice and then try again'))
                        
                    if waybill.move_id.id:                
                        move_obj = self.pool.get('account.move')
                        if waybill.move_id.state != 'draft':
                            move_obj.button_cancel(cr, uid, [waybill.move_id.id]) 
                        move_obj.unlink(cr, uid, [waybill.move_id.id])
                    
                    waybill_obj.write(cr, uid, record_id, {'move_id' : False, 'state':'cancel', 'cancelled_by':uid,'date_cancelled':time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)})
          
                    if record.copy_waybill:                        
                        default ={} 
                        default.update({'replaced_waybill_id': waybill.id,'move_id':False })
                        if record.sequence_id.id:
                            default.update({'sequence_id': record.sequence_id.id })
                        if record.date_order:
                            default.update({'date_order': record.date_order })
                        waybill=waybill_obj.copy(cr, uid, record_id[0], default=default)
        return {'type': 'ir.actions.act_window_close'}

tms_waybill_cancel()