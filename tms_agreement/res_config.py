# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Business Applications
#    Copyright (C) 2004-2012 OpenERP S.A. (<http://openerp.com>).
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

from osv import fields, osv
import pooler
from tools.translate import _

class tms_configuration(osv.osv_memory):
    _name = 'tms.configuration'
    _description = 'configuration for TMS Module'
    _columns = {
        'period_day': fields.integer('Period Day', size=2, help="Defines the day to close the accounting period accounts for the indirect expenses this day must be between 1 and 15"),
    }

    
    _defaults = {
        'period_day': 15,
    }

tms_configuration()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
