# -*- coding: utf-8 -*-
# Copyright 2016, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

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
