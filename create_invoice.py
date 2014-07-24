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

from osv import osv, fields
import time
from datetime import datetime, date
from osv.orm import browse_record, browse_null
from osv.orm import except_orm
from tools.translate import _
from tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
import decimal_precision as dp
import netsvc
import openerp

class tms_maintenance_order_activity_invoice(osv.osv_memory):

    _name = 'tms.maintenance.order.activity.invoice'
    _description = 'Create Invoices from External Workshop Supplier'
###################################################################################################        

    ########## Metodos para crear la factura ##########
    def button_generate_invoices(self,cr,uid,ids,context=None):
        this = self.get_current_instance(cr, uid, ids)
        
        record_ids =  context.get('active_ids',[])
        actividades = self.pool.get('tms.maintenance.order.activity').browse(cr, uid, record_ids)

        self.create_invoices_from_activities_not_invoice_and_done(cr,uid,ids, actividades)
        return True

    def create_invoices_from_activities_not_invoice_and_done(self,cr,uid,ids, activities):
        partners = []

        for activity in activities:
            if not activity.supplier_id.id in partners:
                partners.append(activity.supplier_id)

        for partner in partners:
            activities_to_partner = []
            for activity in activities:
                if activity['supplier_id']['id'] == partner['id']:
                    activities_to_partner.append(activity)
            ###Construir las facturas basadas en este parner
            invoice_obj = self.create_invoice_based_by_activities(cr,uid,ids, partner, activities_to_partner)            
            ################################################################################
            #print 'Parner : '+str(partner)+str(', ........... '+str(activities_to_partner))


    def create_invoice_based_by_activities(self,cr,uid,ids, partner, activities, context=None):

        invoice_lines = [] 

        ### Diccionarios descripcion Factura
        invoice_origin_description = []
        invoice_origin_description_string = '' 

        ##Se generan los Diccionarios de Inv_line vasados en la lista de actividades
        for activity in activities: 
            #print "activity:\n- - - - - - - - - - - - - - - -\n", activity
        
            #a = activity.product_id.product_tmpl_id.property_account_expense.id
            a = activity.maintenance_order_id.product_id.property_stock_production.valuation_out_account_id.id
            #if not a:
            #    a = activity.product_id.categ_id.property_account_expense_categ.id
            if not a:
                raise osv.except_osv(_('Error !'),
                        _('There is no expense account defined ' \
                          'for production location of product: "%s" (id:%d)') % \
                                (activity.maintenance_order_id.product_id.name, activity.maintenance_order_id.product_id.id,))

            a = self.pool.get('account.fiscal.position').map_account(cr, uid, False, a)
            
            descripcion = activity['maintenance_order_id']['name'] + ', ' + activity['product_id']['name_template']
            inv_line = (0,0,{
                        'name'      : descripcion, #Descripcion
                        'origin'    : activity.maintenance_order_id.product_id.name_template,
                        'account_id': a,
                        'price_unit': activity['cost_service_external']+activity['parts_cost_external'],
                        'quantity'  : 1,
                        'uos_id'    : activity.maintenance_order_id.product_id.uos_id.id,
                        'product_id': activity['product_id']['id'],
                        'invoice_line_tax_id': [(6, 0, [x.id for x in activity.maintenance_order_id.product_id.supplier_taxes_id])],
                        'note'      : _('Invoice Created from Maintenance External Workshop Tasks'),
                        'account_analytic_id': False,
                       })
            invoice_lines.append(inv_line)

            if not activity['maintenance_order_id'] in invoice_origin_description:
                invoice_origin_description.append(activity['maintenance_order_id'])
                invoice_origin_description_string = str(activity['maintenance_order_id']['name'])+str(', ')+str(invoice_origin_description_string) 

        #################### Generar La Factura ################################

        journal_id = self.pool.get('account.journal').search(cr, uid, [('type', '=', 'purchase')], context=None)
        journal_id = journal_id and journal_id[0] or False
        
        
        vals = {    
                    'name'              : 'Invoice TMS Maintenance',
                    'origin'            : invoice_origin_description_string,
                    'type'              : 'in_invoice',
                    'journal_id'        : journal_id,
                    'reference'         : 'Maintenance Activities Invoice',
                    'account_id'        : partner.property_account_payable.id,
                    'partner_id'        : partner.id,
                    'address_invoice_id': self.pool.get('res.partner').address_get(cr, uid, [partner.id], ['default'])['default'],
                    'address_contact_id': self.pool.get('res.partner').address_get(cr, uid, [partner.id], ['default'])['default'],
                    'invoice_line'      : [x for x in invoice_lines],                      #account.invoice.line
                    #'currency_id'       : data[1],                                     #res.currency
                    'comment'           : 'Sin Comentarios',
                    #'payment_term'      : pay_term,                                    #account.payment.term
                    'fiscal_position'   : partner.property_account_position.id,
                    'date_invoice'      : time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                }

        invoice_id = self.pool.get('account.invoice').create(cr, uid, vals)
        invoice_obj= self.pool.get('account.invoice').browse(cr,uid,ids,invoice_id)


        #################### Direccionar la Factura generada a las actividades ################################
        for activity in activities:
            activity.write({'invoice_id':invoice_id, 'invoiced':True})
        return invoice_obj


    def get_current_instance(self, cr, uid, ids):
        lines = self.browse(cr,uid,ids)
        obj = None
        for i in lines:
            obj = i
        return obj
 
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
