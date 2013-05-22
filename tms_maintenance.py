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



# Modificamos el objeto Vehiculo para agregar los campos requeridos para MRO
class fleet_vehicle(osv.osv):
    _name = 'fleet.vehicle'
    _inherit = ['fleet.vehicle']
#    _description = "All motor/trailer units"


    _columns = {
# Pendiente de construir los objetos relacionados
        'tires_number': openerp.osv.fields.integer('Number of Tires'),
        'tires_extra': openerp.osv.fields.integer('Number of Extra Tires'),
        'maintenance_cycle_id': openerp.osv.fields.many2one('product.product', 'Maintenance Program', required=True, domain=[('tms_category','=','maint_service_program')]),
        'last_maint_service': openerp.osv.fields.function(_get_last_maint_service, method=True, type="char", string='Last Maintenance Service'),
        'next_maint_service': openerp.osv.fields.many2one('tms.maintenance.cycle.service', 'Next Maintenance ServiceCompany', required=False),
        

    }

    _defaults = {
        'maintenance_cycle_by' 
    	}
