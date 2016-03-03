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
import time
from datetime import datetime, date
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
import openerp.addons.decimal_precision as dp
from openerp import netsvc
from pytz import timezone


# Waybill Category
class tms_waybill_category(osv.osv):
    _name = 'tms.waybill.category'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = 'Waybill Categories'

    _columns = {
        'shop_id'     : fields.many2one('sale.shop', 'Shop'),
        'company_id'  : fields.related('shop_id','company_id',type='many2one',relation='res.company',string='Company',store=True,readonly=True),
        'name'        : fields.char('Name', size=64, required=True),
        'description' : fields.text('Description'),
        'active'      : fields.boolean('Active'),
        }

    _defaults = {
        'active' : True,
        }
