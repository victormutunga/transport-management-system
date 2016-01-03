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
import decimal_precision as dp
from tools.translate import _
import openerp

# Extra data fields for Waybills & Agreement
# Factors
class tms_factor(osv.osv):
    _name = "tms.factor"
    _inherit = "tms.factor"
    _columns = {        
        'agreement_id': openerp.osv.fields.many2one('tms.agreement', 'Agreement', required=False, ondelete='cascade'),# select=True, readonly=True),
        'sequence': openerp.osv.fields.integer('Sequence', help="Gives the sequence calculation for these factors."),
        'notes': openerp.osv.fields.text('Notes'),
        'control': openerp.osv.fields.boolean('Control'),

    }

tms_factor()

#class tms_agreement(osv.osv):
#    _inherit = 'tms.agreement'

#    _columns = {

#        'agreement_customer_factor': openerp.osv.fields.one2many('tms.factor', 'agreement_id', 'Agreement Customer Charge Factors', domain=[('category', '=', 'customer')], states={'confirmed': [('readonly', True)],'done':[('readonly',True)],'cancel':[('readonly',True)]}), 
#        'agreement_supplier_factor': openerp.osv.fields.one2many('tms.factor', 'agreement_id', 'Agreement Supplier Payment Factors', domain=[('category', '=', 'supplier')], states={'confirmed': [('readonly', True)],'done':[('readonly',True)],'cancel':[('readonly',True)]}),
#        'agreement_driver_factor': openerp.osv.fields.one2many('tms.factor', 'agreement_id', 'Agreement Driver Payment Factors', domain=[('category', '=', 'driver')], states={'confirmed': [('readonly', True)],'done':[('readonly',True)],'cancel':[('readonly',True)]}),

#    }

#tms_agreement()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
