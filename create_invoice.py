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
import tools

class create_invoice(osv.Model):
    _name = 'create.invoice'
    _description = "Order Analisys Tms"
    _rec_name='activity_name'
    _auto = False
    _description = 'Order Maintenace Analisys 1'

########################### Columnas : Atributos #######################################################################
    _columns = {
        ######## Integer ###########
        'id':   fields.integer('Activity ID'),

        ######## Char ###########
        'activity_name':   fields.char('Activity'),
        'order_name':      fields.char('Order'),
        'order_id':        fields.char('Order ID'),

        ######## Float ###########
        'cost_manpower':        fields.float('Cost Manpower'),
        'cost_material':        fields.float('Cost Material'),
        'hours':                fields.float('Hours'),

        ######## Date ###########
        'date_begin':       fields.datetime('Date Begin'),
        'date_end':         fields.datetime('Date End'),

        ######## Many2One ###########
        'unit_id':     fields.many2one('fleet.vehicle','Unit'),
        'driver_id':   fields.many2one('hr.employee','Driver'),
        'activity_id': fields.many2one('tms.maintenance.order.activity','Activity'),
        'supplier_id': fields.many2one('res.partner','Supplier'),
    }
   

########################### Metodos ####################################################################################

    def init(self, cr):
        tools.drop_view_if_exists(cr,'create_invoice')
        cr.execute("""
            create or replace view create_invoice as (

select 
	(select p.name_template  from product_product as p where p.id = activity.product_id) as activity_name,
	(activity.id                                                                       ) as activity_id,
	(activity.id                                                                       ) as id,

    (select u.id            from fleet_vehicle as u where u.id=o.unit_id)                as unit_id,
    (select u.name          from fleet_vehicle as u where u.id=o.unit_id)                as unit_name,

    (select e.id            from hr_employee   as e where e.id=o.driver_id)              as driver_id,
    (select e.name_related  from hr_employee   as e where e.id=o.driver_id)              as driver_name,

    (select r.id   from res_partner   as r where r.id = activity.supplier_id)   as supplier_id,

	activity.date_start_real                                                             as date_begin,
	activity.date_end_real                                                               as date_end,
	activity.hours_real                                                                  as hours,

	activity.cost_service                                                                as cost_manpower,
	activity.parts_cost                                                                  as cost_material,
	
	o.name                                                                               as order_name,
	o.id                                                                                 as order_id,
	(select i.state from account_invoice as i where i.id = activity.invoice_id)	     as invoice_state,
	(select i.id from account_invoice as i where i.id = activity.invoice_id)	     as invoice_id,
	activity.invoiced                                                                    as invoiced
	
                                                                  
from tms_maintenance_order_activity as activity, tms_maintenance_order as o
where (activity.maintenance_order_id = o.id and activity.external_workshop and activity.state like 'done' and not activity.invoiced) 
	or (activity.maintenance_order_id = o.id and activity.external_workshop and activity.state like 'done' and activity.invoiced and (select i.state from account_invoice as i where i.id = activity.invoice_id) like 'cancel') 
	or (activity.maintenance_order_id = o.id and activity.external_workshop and activity.state like 'done' and activity.invoiced and (select i.id from account_invoice as i where i.id = activity.invoice_id) is null and invoiced) 
order by maintenance_order_id   
                
            )
        """)
    
create_invoice()



##################################################################################################################################
##################################################################################################################################
##################################################################################################################################
##################################################################################################################################
##################################################################################################################################
##################################################################################################################################
##################################################################################################################################
##################################################################################################################################
##################################################################################################################################
##################################################################################################################################

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

class create_invoice_now(osv.osv_memory):

    _name = 'create.invoice.now'
    _description = 'Make Invoices from External Workshop Supplier'
###################################################################################################        

    ########## Metodos para crear la factura ##########
    def button_generate_invoices(self,cr,uid,ids,context=None):
        this = self.get_current_instance(cr, uid, ids)

        #activities_external_done_not_invoice = self.get_activities_external_done_not_invoice(cr,uid,ids,context)

        #activities = activities_external_done_not_invoice 
        
        record_ids =  context.get('active_ids',[])
        ##print 'eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee'
        #print 'eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee'
        #print 'eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee'
        #print 'eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee: '+str(record_ids)

        actividades = []
        for line in self.pool.get('create.invoice').browse(cr,uid,record_ids):
            actividades.append(line['activity_id'])

        #print 'eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee'
        #print 'eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee'
        #print 'eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee'
        #print 'eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee: '+str(actividades)
        

        self.create_invoices_from_activities_not_invoice_and_done(cr,uid,ids, actividades)
        return True

    def create_invoices_from_activities_not_invoice_and_done(self,cr,uid,ids, activities):
        partners = []

        for activity in activities:
            if not activity['supplier_id'] in partners:
                partners.append(activity['supplier_id'])
        #print '++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ partner: '+str(partners)

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

        ### Diccionarios de Invoice Lines
        ### Diccionarios de Invoice Lines
        ### Diccionarios de Invoice Lines
        invoice_lines = [] 

        ### Diccionarios descripcion Factura
        invoice_origin_description = []
        invoice_origin_description_string = '' 

        ##Se generan los Diccionarios de Inv_line vasados en la lista de actividades
        ##Se generan los Diccionarios de Inv_line vasados en la lista de actividades
        ##Se generan los Diccionarios de Inv_line vasados en la lista de actividades
        for activity in activities: 
            #print "activity:\n- - - - - - - - - - - - - - - -\n", activity
            
            a = activity.product_id.product_tmpl_id.property_account_expense.id
            if not a:
                a = activity.product_id.categ_id.property_account_expense_categ.id
            if not a:
                raise osv.except_osv(_('Error !'),
                        _('There is no expense account defined ' \
                          'for this product: "%s" (id:%d)') % \
                                (activity.product_id.name, activity.product_id.id,))

            a = self.pool.get('account.fiscal.position').map_account(cr, uid, False, a)
            
            descripcion = activity['maintenance_order_id']['name'] + ', ' + activity['product_id']['name_template']
            inv_line = (0,0,{
                        #'name': activity['product_id']['name_template'],
                        'name': descripcion, #Descripcion
                        'origin': activity['maintenance_order_id']['product_id']['name_template'],
                        'account_id': a,
                        'price_unit': activity['cost_service']+activity['parts_cost'],
                        'quantity': 1,
                        'uos_id': activity['product_id'].uos_id.id,
                        'product_id': activity['product_id']['id'],
                        'invoice_line_tax_id': [(6, 0, [x.id for x in activity['product_id'].supplier_taxes_id])],
                        'note': 'Notasss',
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
