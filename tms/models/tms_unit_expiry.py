
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
# Units for Transportation EXPIRY EXTRA DATA


class tms_unit_expiry(osv.osv):
    _name = "tms.unit.expiry"
    _description = "Expiry Extra Data for Units"

    _columns = {
        'unit_id'       : fields.many2one('fleet.vehicle', 'Unit Name', required=True, ondelete='cascade', select=True,),        
        'expiry_id'     :fields.many2one('tms.unit.category', 'Field', domain="[('type','=','expiry')]", required=True),
        'extra_value'   : fields.date('Value', required=True),
        'name'          : fields.char('Valor', size=10, required=True),
        }

    _sql_constraints = [
        ('name_uniq', 'unique(unit_id,expiry_id)', 'Expiry Data Field must be unique for each unit !'),
        ]

    def on_change_extra_value(self, cr, uid, ids, extra_value):
        return {'value': {'name': extra_value[8:] + '/' + extra_value[5:-3] + '/' + extra_value[:-6]}}
