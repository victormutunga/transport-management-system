# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Travel Reports',
    'summary': 'View and create reports',
    'category': 'Accounting',
    'description': """
Accounting Reports
====================
    """,
    'depends': ['account', 'tms'],
    'data': [
        'data/init.yml',
        'data/tms_general_report_data.xml',
        'views/tms_manager_report.xml',
    ],
    'qweb': [
        'static/src/xml/tms_report_backend.xml',
    ],
    'auto_install': True,
    'installable': True,
    'license': 'OEEL-1',
}
