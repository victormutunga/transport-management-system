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

class tms_analisys_01(osv.Model):
    _name = 'tms.analisys.01'
    _description = "Order Analisys Tms"
    _auto = False
    _description = 'Order Maintenace Analisys 1, Order'

########################### Columnas : Atributos #######################################################################
    _columns = {
        ######## Integer ###########
        'id':   fields.integer('ID order'),

        ######## Char ###########
        'name':        fields.char('Order Maintenance'),
        'user_name':   fields.char('User Name'),
        'unit_name':   fields.char('Unit Name'),
        'driver_name': fields.char('Driver Name'),

        ######## Float ###########
        'manpower_cost':        fields.float('Manpower Cost'),
        'material_cost':        fields.float('Material Cost'),

        ######## Date ###########
        'date':       fields.datetime('Date'),
        'date_start': fields.datetime('Date Start'),
        'date_end':   fields.datetime('Date End'),

        ######## Many2One ###########
        'user_id':   fields.many2one('res.users','User ID'),
        'unit_id':   fields.many2one('fleet.vehicle','Unit ID'),
        'driver_id': fields.many2one('hr.employee','Driver ID'),
    }
    
########################### Metodos ####################################################################################

    def init(self, cr):
        tools.drop_view_if_exists(cr,'tms_analisys_01')
        cr.execute("""
            create or replace view tms_analisys_01 as (

select id as id, name as name, date as date,
       user_id as user_id,     (select u.login         from res_users     as u where u.id=o.user_id)   as user_name,
       unit_id as unit_id,     (select u.name          from fleet_vehicle as u where u.id=o.unit_id)   as unit_name,
       driver_id as driver_id, (select e.name_related  from hr_employee   as e where e.id=o.driver_id) as driver_name,
       date_start_real as date_start,
       date_end_real   as date_end,
       cost_service as manpower_cost,
       parts_cost   as material_cost
from tms_maintenance_order as o
where o.state like 'done'
order by o.id           
                
            )
        """)
    
tms_analisys_01()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
