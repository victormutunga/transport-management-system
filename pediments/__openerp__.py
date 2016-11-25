# -*- coding: utf-8 -*-
# © <2016> <Jarsa Sistemas, S.A. de C.V.>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Pediments",
    "version": "9.0.0.1.0",
    "category": "Transport",
    "author": "Jarsa Sistemas",
    "website": "https://www.jarsa.com.mx",
    "depends": ["tms"],
    "summary": "Management Pediments for Carriers,"
               "Trucking and other companies",
    "license": "AGPL-3",
    "data": [
        'security/ir.model.access.csv',
        'views/tms_pediments_view.xml',
        'views/tms_waybill_view.xml',
    ],
    "demo": [],
    "application": True,
    "installable": True,
}
