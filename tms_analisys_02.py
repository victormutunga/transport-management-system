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

class tms_analisys_02(osv.Model):
    _name = 'tms.analisys.02'
    _description = "Order Analisys Tms"
    _rec_name='activity_name'
    _auto = False
    _description = 'Order Maintenace Analisys 2'

########################### Columnas : Atributos #######################################################################
    _columns = {
        ######## Integer ###########
        'id':   fields.integer('Activity ID'),

        ######## boolean ###########
        'external_workshop':   fields.boolean('External'),

        ######## Char ###########
        'activity_name':   fields.char('Activity'),
        'order_name':      fields.char('Order'),
        'order_id':        fields.char('Order ID'),
        'invoice_name':    fields.char('Invoice Name'),
        'partner_name':    fields.char('Partner Name'),
        'unit_name':       fields.char('Unit Name'),

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
        'invoice_id':  fields.many2one('account.invoice','Invoice ID'),
        'partner_id':  fields.many2one('res.partner','Partner ID'),
        
        ########Related ###########
        'supplier_invoice_number': fields.char('Invoice Number', readonly=True),
    }
    
########################### Metodos ####################################################################################

    def init(self, cr):
        tools.drop_view_if_exists(cr,'tms_analisys_02')
        cr.execute("""
            create or replace view tms_analisys_02 as (

select 
	(select p.name_template  from product_product as p where p.id = activity.product_id) as activity_name,
	(activity.id                                                                       ) as activity_id,
	(activity.id                                                                       ) as id,

    (select u.id            from fleet_vehicle as u where u.id=o.unit_id)                as unit_id,
    (select u.name          from fleet_vehicle as u where u.id=o.unit_id)                as unit_name,

    (select e.id            from hr_employee   as e where e.id=o.driver_id)              as driver_id,
    (select e.name_related  from hr_employee   as e where e.id=o.driver_id)              as driver_name,

	activity.date_start_real                                                             as date_begin,
	activity.date_end_real                                                               as date_end,
	activity.hours_real                                                                  as hours,

	activity.cost_service                                                                as cost_manpower,
	activity.parts_cost                                                                  as cost_material,
	
	o.name                                                                               as order_name,
	o.id                                                                                 as order_id,

	activity.external_workshop							                                 as external_workshop,
	
	(select i.id from account_invoice as i where i.id = activity.invoice_id)	                    as invoice_id,
	(select i.name from account_invoice as i where i.id = activity.invoice_id)	                    as invoice_name,
	(select i.supplier_invoice_number from account_invoice as i where i.id = activity.invoice_id)	as supplier_invoice_number,

	(select p.id from res_partner as p where activity.supplier_id = p.id)                as partner_id,
	(select p.name from res_partner as p where activity.supplier_id = p.id)              as partner_name

                                                                  
from tms_maintenance_order_activity as activity, tms_maintenance_order as o
where activity.state like 'done' and activity.maintenance_order_id = o.id and o.state like 'done'
order by maintenance_order_id        
                
            )
        """)
    
tms_analisys_02()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
