# -*- coding: utf-8 -*-
# Copyright 2012, Israel Cruz Argil, Argil Consulting
# Copyright 2016, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "TMS - Driver License Management",
    "summary": "Manage Driver license expiration and adds a constraint to "
               "avoid Dispatching Travels when Driver License is expired",
    "version": "9.0.1.0.0",
    "category": "TMS",
    "website": "https://www.jarsa.com.mx/",
    "author": "Argil Consulting, Jarsa Sistemas",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "tms",
    ],
    "data": [
        "views/hr_employee_view.xml",
        "data/ir_config_parameter.xml",
    ],
    'external_dependencies': {
        'python': [
            'sodapy',
        ],
    },
    "demo": [],
}
