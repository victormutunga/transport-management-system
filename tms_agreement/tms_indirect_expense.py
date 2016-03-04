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
from tools.translate import _
from tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
import decimal_precision as dp
import netsvc
import openerp

class tms_indirect_expense(osv.osv):
    _name = 'tms.indirect.expense'
    _description = 'Indirect Expense for Agreement'
    _rec_name='product_id'

    _columns = {
        'product_id'        : openerp.osv.fields.many2one('product.product', 'Product',domain=[('tms_category', '=','indirect_expense')] ),
        'agreement_id'		: openerp.osv.fields.many2one('tms.agreement', 'Agreement', required=False, ondelete='cascade', select=True, readonly=True),
#        'period_day'        : openerp.osv.fields.integer('Period Day', size=2, help="Defines the day to close the accounting period accounts for the indirect expenses this day must be between 1 and 15"),
        'description'       : openerp.osv.fields.related('product_id', 'product_tmpl_id', 'description', type="text", string="Descripcion", readonly=True),
        'notes'             : openerp.osv.fields.text('Notes'),
        'total_mount_indirect'		: openerp.osv.fields.float('Total Mount', digits=(16, 2)),
        'automatic'         : openerp.osv.fields.boolean('Automatic', help="If this field is enabled the amount of expenses will be calculated automatically"),
            }

    def get_current_instance(self, cr, uid, id):
        line = self.browse(cr,uid,id)
        obj = None
        for i in line:
            obj = i
        return obj


    _defaults = {
        'automatic': False,
     
    }
tms_indirect_expense()
