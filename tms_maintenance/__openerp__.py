# -*- encoding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012 HESATEC (<http://www.hesatecnica.com>).
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
###############################################################################

{   
    "name" : "Fleet Maintenance Workshop Management",
    "version" : "1.0",
    "category" : "Vertical",
    'complexity': "normal",
    "author" : "HESATEC",
    "website": "http://www.hesatecnica.com",
    "depends" : ["tms","stock_move_entries"],
    "description": """
Fleet Maintenance Workshop Management
=========================================

This application allows you to manage an Fleet  Maintenance Workshop, very useful when Compnay has its own Maintenance Workshop. 

It handles full Maintenance Workflow:
Opening Maintenance Order => Warehouse Integration => Closing Maintenance Order

Also, you can manage:
- Several Workshops
- Preventive Maintenance Cycles
- Corrective Maintenance
- Warehouse Integration for spare parts

Takes from Freight Management Module:
- Vehicles
- Trucks Red Tapes
- Truck Odometers

""",
    "data" : [
                'security/tms_security.xml',
                'security/ir.model.access.csv',
                'views/ir_config_parameter.xml',
                'views/product_view.xml',
                'views/sale_view.xml',
                'views/stock_view.xml',
                'views/tms_activity_control_time_view.xml',
                'views/tms_analisys_01_view.xml',
                'views/tms_analisys_02_view.xml',
                'views/tms_analisys_03_view.xml',
                'views/tms_analisys_04_view.xml',
                # 'views/tms_analisys_05_view.xml',
                'views/tms_maintenance_driver_report_view.xml',
                'views/tms_maintenance_order_activity_view.xml',
                'views/tms_maintenance_order_view.xml',
                'views/tms_maintenance_program_view.xml',
                'views/tms_maintenance_view.xml',
                'views/tms_mini_esqueleto_view.xml',
                'views/tms_product_line_view.xml',
                'views/tms_time_view.xml',
                   ], 
    "active": False,
    'application': True,
    "installable": True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

