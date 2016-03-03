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
import time


# Units Kits
class tms_unit_kit(osv.osv):
    _name = "tms.unit.kit"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "Units Kits"

    _columns = {
        'name'          : fields.char('Name', size=64, required=True),
        'unit_id'       : fields.many2one('fleet.vehicle', 'Unit', required=True),
        'unit_type'     : fields.related('unit_id', 'unit_type_id', type='many2one', relation='tms.unit.category', string='Unit Type', store=True, readonly=True),
        'trailer1_id'   : fields.many2one('fleet.vehicle', 'Trailer 1', required=True),
        'trailer1_type' : fields.related('trailer1_id', 'unit_type_id', type='many2one', relation='tms.unit.category', string='Trailer 1 Type', store=True, readonly=True),
        'dolly_id'      : fields.many2one('fleet.vehicle', 'Dolly'),
        'dolly_type'    : fields.related('dolly_id', 'unit_type_id', type='many2one', relation='tms.unit.category', string='Dolly Type', store=True, readonly=True),
        'trailer2_id'   : fields.many2one('fleet.vehicle', 'Trailer 2'),
        'trailer2_type' : fields.related('trailer2_id', 'unit_type_id', type='many2one', relation='tms.unit.category', string='Trailer 2 Type', store=True, readonly=True),
        'employee_id'   : fields.many2one('hr.employee', 'Driver', domain=[('tms_category', '=', 'driver')]),
        'date_start'    : fields.datetime('Date start', required=True),
        'date_end'      : fields.datetime('Date end', required=True),
        'notes'         : fields.text('Notes'),
        'active'            : fields.boolean('Active'),        
        }

    _defaults = {
        'active' : lambda *a : True,
    }

    def _check_expiration(self, cr, uid, ids, context=None):
        for record in self.browse(cr, uid, ids, context=context):
            date_start = record.date_start
            date_end   = record.date_end
            
            sql = 'select name from tms_unit_kit where id <> ' + str(record.id) + ' and unit_id = ' + str(record.unit_id.id) \
                    + ' and (date_start between \'' + date_start + '\' and \'' + date_end + '\'' \
                        + ' or date_end between \'' + date_start + '\' and \'' + date_end + '\');' 

            cr.execute(sql)
            data = filter(None, map(lambda x:x[0], cr.fetchall()))
            if len(data):
                raise osv.except_osv(_('Validity Error !'), _('You cannot have overlaping expiration dates for unit %s !\n' \
                                                                'This unit is overlaping Kit << %s >>')%(record.unit_id.name, data[0]))
            if record.dolly_id.id:
                sql = 'select name from tms_unit_kit where id <> ' + str(record.id) + ' and dolly_id = ' + str(record.dolly_id.id) \
                        + ' and (date_start between \'' + date_start + '\' and \'' + date_end + '\'' \
                            + ' or date_end between \'' + date_start + '\' and \'' + date_end + '\');' 

                cr.execute(sql)
                data = filter(None, map(lambda x:x[0], cr.fetchall()))
                if len(data):
                    raise osv.except_osv(_('Validity Error !'), _('You cannot have overlaping expiration dates for dolly %s !\n' \
                                                                    'This dolly is overlaping Kit << %s >>')%(record.dolly_id.name, data[0]))
            sql = 'select name from tms_unit_kit where id <> ' + str(record.id) + ' and (trailer1_id = ' + str(record.trailer1_id.id) + 'or trailer2_id = ' + str(record.trailer1_id.id) + ')' \
                    + ' and (date_start between \'' + date_start + '\' and \'' + date_end + '\'' \
                        + ' or date_end between \'' + date_start + '\' and \'' + date_end + '\');' 
            cr.execute(sql)
            data = filter(None, map(lambda x:x[0], cr.fetchall()))
            if len(data):
                raise osv.except_osv(_('Validity Error !'), _('You cannot have overlaping expiration dates for trailer %s !\n' \
                                                                'This trailer is overlaping Kit << %s >>')%(record.trailer1_id.name, data[0]))
            if record.trailer2_id.id:
                sql = 'select name from tms_unit_kit where id <> ' + str(record.id) + ' and (trailer1_id = ' + str(record.trailer2_id.id) + 'or trailer2_id = ' + str(record.trailer2_id.id) + ')' \
                        + ' and (date_start between \'' + date_start + '\' and \'' + date_end + '\'' \
                            + ' or date_end between \'' + date_start + '\' and \'' + date_end + '\');' 
                cr.execute(sql)
                data = filter(None, map(lambda x:x[0], cr.fetchall()))  
                if len(data):
                    raise osv.except_osv(_('Validity Error !'), _('You cannot have overlaping expiration dates for trailer %s !\n' \
                                                                    'This trailer is overlaping Kit << %s >>')%(record.trailer2_id.name, data[0]))
            return True

    _constraints = [
        (_check_expiration,
            'The expiration is overlaping an existing Kit for this unit!',
            ['date_start'])
    ]

    _sql_constraints = [
        ('name_uniq', 'unique(unit_id,name)', 'Kit name number must be unique for each unit !'),
        ]
    _order = "name desc, date_start desc"

    def on_change_tms_unit_id(self, cr, uid, ids, tms_unit_id):
        res = {'value': {'date_start': time.strftime('%Y-%m-%d %H:%M')}}
        if not (tms_unit_id):
            return res
        cr.execute("select date_end from tms_unit_kit where id=%s order by  date_end desc limit 1", tms_unit_id)
        date_start = cr.fetchall()
        if not date_start:
            return res
        else:
            return {'value': {'date_start': date_start[0]}} 

    def on_change_active(self, cr, uid, ids, active):
        if active:
            return {}
        return {'value': {'date_end' : time.strftime('%d/%m/%Y %H:%M:%S')}}