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


# Extra data fields for Waybills & Negotiations
class fleet_vehicle_model(osv.osv):
    _name = "fleet.vehicle.model"
    _inherit = "fleet.vehicle.model"
    _columns = {        
        'agreement_id': openerp.osv.fields.many2one('tms.agreement', 'Agreement', required=False, ondelete='cascade', select=True, readonly=True),
        
    }

fleet_vehicle_model()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
