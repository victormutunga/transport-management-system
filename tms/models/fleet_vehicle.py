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
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
import time


# Units for Transportation
class fleet_vehicle(osv.osv):
    _name = 'fleet.vehicle'
    _inherit = ['fleet.vehicle']
    _description = "All motor/trailer units"

    def _get_current_odometer(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for record in self.browse(cr, uid, ids, context=context):            
            odom_obj = self.pool.get('fleet.vehicle.odometer.device')
            result = odom_obj.search(cr, uid, [('vehicle_id', '=', record.id),('state', '=', 'active')], limit=1, context=None)
            ##print "result: ", result
            if result and result[0]:
                res[record.id] = result[0]
        return res

    _columns = {
        'shop_id': fields.many2one('sale.shop', 'Shop', required=True, readonly=False),
#        'company_id': fields.related('shop_id','company_id',type='many2one',relation='res.company',string='Company',store=True,readonly=True),
        'name': fields.char('Unit Name', size=64, required=True),
        'year_model':fields.char('Year Model', size=64), 
        'unit_type_id':fields.many2one('tms.unit.category', 'Unit Type', domain="[('type','=','unit_type')]"),
#        'unit_brand_id':fields.many2one('tms.unit.category', 'Brand', domain="[('type','=','brand')]"),
#        'unit_model_id':fields.many2one('tms.unit.category', 'Model', domain="[('type','=','model')]"),
        'unit_motor_id':fields.many2one('tms.unit.category', 'Motor', domain="[('type','=','motor')]"),
        'serial_number': fields.char('Serial Number', size=64),
        'vin': fields.char('VIN', size=64),
        'day_no_circulation': fields.selection([
                            ('sunday','Sunday'), 
                            ('monday','Monday'), 
                            ('tuesday','Tuesday'), 
                            ('wednesday','Wednesday'), 
                            ('thursday','Thursday'), 
                            ('friday','Friday'), 
                            ('saturday','Saturday'), 
                            ('none','Not Applicable'), 
                           ], string="Day no Circulation", translate=True),
        'registration': fields.char('Registration', size=64), # Tarjeta de Circulacion
        'gps_supplier_id': fields.many2one('res.partner', 'GPS Supplier', required=False, readonly=False, 
                                            domain="[('tms_category','=','gps'),('is_company', '=', True)]"),
        'gps_id': fields.char('GPS Id', size=64),
        'employee_id': fields.many2one('hr.employee', 'Driver', required=False, domain=[('tms_category', '=', 'driver')], help="This is used in TMS Module..."),
        'fleet_type': fields.selection([('tractor','Motorized Unit'), ('trailer','Trailer'), ('dolly','Dolly'), ('other','Other')], 'Unit Fleet Type', required=True),
        'avg_odometer_uom_per_day'  :fields.float('Avg Distance/Time per day', required=False, digits=(16,2), help='Specify average distance traveled (mi./kms) or Time (Days, hours) of use per day for this'),
        
        'notes'                 : fields.text('Notes'),
        'active'                : fields.boolean('Active'),
        'unit_extradata_ids'    : fields.one2many('tms.unit.extradata', 'unit_id', 'Extra Data'),
        'unit_expiry_ids'       : fields.one2many('tms.unit.expiry', 'unit_id', 'Expiry Extra Data'), 
        'unit_photo_ids'        : fields.one2many('tms.unit.photo', 'unit_id', 'Photos'), 
        'unit_active_history_ids' : fields.one2many('tms.unit.active_history', 'unit_id', 'Active/Inactive History'), 
        'unit_red_tape_ids'     : fields.one2many('tms.unit.red_tape', 'unit_id', 'Unit Red Tapes'), 
        'supplier_unit'         : fields.boolean('Supplier Unit'),
        'supplier_id'           : fields.many2one('res.partner', 'Supplier', required=False, readonly=False, 
                                            domain="[('tms_category','=','none'),('is_company', '=', True)]"),
        'latitude'              : fields.float('Lat', required=False, digits=(20,10), help='GPS Latitude'),
        'longitude'             : fields.float('Lng', required=False, digits=(20,10), help='GPS Longitude'),
        'last_position'         : fields.char('Last Position', size=250),
        'last_position_update'  : fields.datetime('Last GPS Update'),
        'active_odometer'       : fields.float('Odometer', required=False, digits=(20,10), help='Odometer'),
        'active_odometer_id'    : fields.function(_get_current_odometer, type='many2one', relation="fleet.vehicle.odometer.device", string="Active Odometer"),
        'current_odometer_read' : fields.related('active_odometer_id', 'odometer_end', type='float', string='Last Odometer Read', readonly=True),
        'odometer_uom'          : fields.selection([('distance','Distance (mi./km)'),
                                                                ('hours','Time (Hours)'),
                                                                ('days','Time (Days)')], 'Odometer UoM', help="Odometer UoM"),

    }

    _defaults = {
        'fleet_type'  : lambda *a : 'tractor',
        'active'      : True,
        'odometer_uom': lambda *a : 'distance',
    	}

    def _check_extra_data_expiry(self, cr, uid, ids, context=None):
        categ_obj = self.pool.get('tms.unit.category')
        expiry_obj = self.pool.get('tms.unit.expiry')
        recs = categ_obj.search(cr, uid, [('mandatory', '=', 1), ('type', '=', 'expiry')])
        if recs:
            unit_id = self.browse(cr, uid, ids)[0].id
            for rec in categ_obj.browse(cr, uid, recs):
                if not expiry_obj.search(cr, uid, [('expiry_id', '=', rec.id), ('unit_id', '=', unit_id)]):
                    return False
        return True

    _constraints = [
        (_check_extra_data_expiry,
            'You have defined certain mandatory Expiration Extra Data fields that you did not include in this Vehicle record. Please add missing fields.',
            ['unit_expiry_ids'])
        ]

    _sql_constraints = [
            ('name_uniq', 'unique(name)', 'Unit name number must be unique !'),
            ('gps_id_uniq', 'unique(gps_id)', 'Unit GPS ID must be unique !'),
        ]

    def copy(self, cr, uid, id, default=None, context=None):
        unit = self.browse(cr, uid, id, context=context)
        if not default:
            default = {}
        default['name'] = unit['name'] + ' (copy)'
        default['gps_id'] = ''
        default['unit_extradata_ids'] = []
        default['unit_expiry_ids'] = []
        default['unit_photo_ids'] = []
        return super(fleet_vehicle, self).copy(cr, uid, id, default, context=context)

    def create(self, cr, uid, vals, context=None):
        values = vals
        res = super(fleet_vehicle, self).create(cr, uid, values, context=context)
        
        odom_obj = self.pool.get('fleet.vehicle.odometer.device')
        rec = { 'name'          : _('Odometer device created when vehicle %s was created') % (vals['name']),
                'state'         : 'draft',
                'date'          : time.strftime( DEFAULT_SERVER_DATETIME_FORMAT),
                'date_start'    : time.strftime( DEFAULT_SERVER_DATETIME_FORMAT),
                'vehicle_id'    : res,
                'accumulated_start' : 0.0,
                'odometer_start'    : 0.0, 
            }
        odom_id = odom_obj.create(cr, uid, rec)    
        odom_obj.action_activate(cr, uid, [odom_id])
        return res

    def return_action_to_open_tms(self, cr, uid, ids, context=None):
        """ This opens the xml view specified in xml_id for the current vehicle """
        if context is None:
            context = {}
        if context.get('xml_id'):
            res = self.pool.get('ir.actions.act_window').for_xml_id(cr, uid ,'tms', context['xml_id'], context=context)
            res['context'] = context
            res['context'].update({'default_unit_id': ids[0]})
            res['domain'] = [('unit_id','=', ids[0])]
            return res
        return False
