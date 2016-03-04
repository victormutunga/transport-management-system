# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2014 Argil Consulting - http://www.argil.mx
############################################################################
#    Coded by: Israel Cruz Argil (israel.cruz@argil.mx)
############################################################################
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
from tools.translate import _
from datetime import datetime, timedelta
from tools import DEFAULT_SERVER_DATE_FORMAT


class hr_employee_expired_license(osv.osv_memory):
    _name = 'hr.employee.expired_license'
    _description = "Wizard to get Driver's Licenses about to expire"

    
    def _get_date(self, cr, uid, ids, context=None):
        val = self.pool.get('ir.config_parameter').get_param(cr, uid, 'tms_driver_license_notification_x_days', context=context)
        xdays = int(val) or 0
        date = datetime.now()  + timedelta(days=xdays)
        return date.strftime(DEFAULT_SERVER_DATE_FORMAT)
    
    _columns = {
            'date'    : fields.date('Date', required=True),
            'include' : fields.selection([
                                ('all', 'All Drivers (Internal & External)'),
                                ('int', 'Internal Drivers only'),
                                ('ext', 'External Drivers only'),
                                ], 'Include', required=True),
            }

    _defaults = {
        'date'   : _get_date,
        'include' : 'all',
            }
    
    def button_get_licenses_to_expire(self, cr, uid, ids, to_attach=False, context=None):
        """
        To get the date and print the report
        @return : return report
        """
        if context is None:
            context = {}

        
        date = self.browse(cr, uid, ids)[0].date
        include = self.browse(cr, uid, ids)[0].include
        hr_emp_obj = self.pool.get('hr.employee')
        condition = [('tms_driver_license_expiration',"<=", date), ('tms_category','=','driver')]
        if include=='int':
            condition.append(('tms_supplier_driver','=',False))
        elif include=='ext':
            condition.append(('tms_supplier_driver','=',True))
        employee_ids = hr_emp_obj.search(cr, uid, condition, order='tms_driver_license_expiration desc')
        
        if employee_ids:
            datas = {   'ids': employee_ids, 
                        'count': len(employee_ids),
                        'date': date}
            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'hr.employee.expired_licenses.report.webkit',
                'datas': datas,
                }
        else:
            raise osv.except_osv(_('Warning!'), _('There are no Driver Licenses expired or to expire on this date'))

        

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
