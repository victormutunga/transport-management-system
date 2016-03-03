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

# Units PHOTOS


class tms_unit_photo(osv.osv):
    _name = "tms.unit.photo"
    _description = "Units Photos"

    _columns = {
        'unit_id' : fields.many2one('fleet.vehicle', 'Unit Name', required=True, ondelete='cascade'),
        'name': fields.char('Description', size=64, required=True),
        'photo': fields.binary('Photo'),
        }

    _sql_constraints = [
        ('name_uniq', 'unique(unit_id,name)', 'Photo name number must be unique for each unit !'),
        ]