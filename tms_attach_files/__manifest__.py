# -*- coding: utf-8 -*-
# Copyright 2016, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Attach Travel Expense Line Files',
    'summary': 'Attach xml and pdf files to Travel Expenses Lines',
    'description': 'Attach xml and pdf files.',
    'author': 'Jarsa Sistemas',
    'website': 'https://www.jarsa.com.mx',
    'category': 'Transport',
    'version': '10.0.0.2.0',
    'depends': ['tms'],
    'data': [
        'views/tms_expense_line_view.xml'
    ],
    'installable': True,
}
