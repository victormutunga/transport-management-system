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


# Master catalog used for:
# - Unit Types
# - Unit Brands
# - Unit / Motor Models
# - Motor Type
# - Extra Data for Units (Like Insurance Policy, Unit Invoice, etc
# - Unit Status (Still not defined if is keeped or not
# - Documentacion expiraton  for Transportation Units
class tms_unit_category(osv.osv):
    _name = "tms.unit.category"
    _description = "Types, Brands, Models, Motor Type for Transport Units"

    def name_get(self, cr, uid, ids, context=None):
        if not len(ids):
            return []
        reads = self.read(cr, uid, ids, ['name','parent_id'], context=context)
        res = []
        for record in reads:
            name = record['name']
            if record['parent_id']:
                name = record['parent_id'][1]+' / '+name
            res.append((record['id'], name))
        return res

    def _name_get_fnc(self, cr, uid, ids, prop, unknow_none, context=None):
        res = self.name_get(cr, uid, ids, context=context)
        return dict(res)

    _columns = {
        'name': fields.char('Name', size=30, required=True, translate=True),
        'complete_name': fields.function(_name_get_fnc, method=True, type="char", size=300, string='Complete Name', store=True),
        'parent_id': fields.many2one('tms.unit.category','Parent Category', select=True),
        'child_id': fields.one2many('tms.unit.category', 'parent_id', string='Child Categories'),
        'sequence': fields.integer('Sequence', help="Gives the sequence order when displaying this list of categories."),
        'type': fields.selection([
                            ('view','View'), 
                            ('unit_type','Unit Type'), 
                            ('brand','Motor Brand'), 
                            ('motor','Motor Model'), 
                            ('extra_data', 'Extra Data'),
                            ('unit_status','Unit Status'),
                            ('expiry','Expiry'),
                            ('active_cause','Active / Inactive Causes'),
                            ('red_tape','Red Tape Types'),
                        ], 'Category Type',required=True, help="""Category Types:
 - View: Use this to define tree structure
 - Type: Use this to define Unit types, like Tractor, Trailers, dolly, van, etc.
 - Brand: Units brands
 - Motor: Motors
 - Extra Data: Use to define several extra fields for unit catalog.
 - Expiry: Use it to define several extra fields for units related to document expiration (Ex. Insurance Validity, Plates Renewal, etc)
 - Active / Inactive Causes: Use to define causes for a unit to be Active / Inactive (Ex: Highway Accident, Sold, etc)
 - Red Tape Types: Use it to define all kind of Red Tapes like Unit registration, Traffic Violations, etc.
"""
                ),
        'fuel_efficiency_drive_unit': fields.float('Fuel Efficiency Drive Unit', required=False, digits=(14,4)),
        'fuel_efficiency_1trailer': fields.float('Fuel Efficiency One Trailer', required=False, digits=(14,4)),
        'fuel_efficiency_2trailer': fields.float('Fuel Efficiency Two Trailer', required=False, digits=(14,4)),
        'notes': fields.text('Notes'),
        'active': fields.boolean('Active'),
        'mandatory': fields.boolean('Mandatory', help="This field is used only when field <Category Type> = expiry"),
        'company_id': fields.many2one('res.company', 'Company', required=False),
    }

    _defaults = {
#        'type' : lambda *a : 'unit_type',
        'active': True,
    }

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Category name number must be unique !'),
        ]

    _order = "sequence"

    def _check_recursion(self, cr, uid, ids, context=None):
        level = 100
        while len(ids):
            cr.execute('select distinct parent_id from tms_unit_category where id IN %s',(tuple(ids),))
            ids = filter(None, map(lambda x:x[0], cr.fetchall()))
            if not level:
                return False
            level -= 1
        return True

    _constraints = [
        (_check_recursion, 'Error ! You can not create recursive categories.', ['parent_id'])
    ]

    def child_get(self, cr, uid, ids):
        return [ids]

    def copy(self, cr, uid, id, default=None, context=None):
        categ = self.browse(cr, uid, id, context=context)
        if not default:
            default = {}
        default['name'] = categ['name'] + ' (copy)'
        return super(tms_unit_category, self).copy(cr, uid, id, default, context=context)


