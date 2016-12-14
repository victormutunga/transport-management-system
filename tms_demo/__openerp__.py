# -*- coding: utf-8 -*-
# Copyright 2012, Israel Cruz Argil, Argil Consulting
# Copyright 2016, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "TMS Demo Data",
    "version": "9.0.0.1.0",
    "category": "Transport",
    "author": "Argil Consulting, Jarsa Sistemas",
    "website": "http://www.argil.mx, https://www.jarsa.com.mx",
    "depends": ["tms", "l10n_generic_coa"],
    "summary": "Demo Data for TMS",
    "license": "AGPL-3",
    "demo": [
        'demo/account_account.xml',
        'demo/res_partner.xml',
        'demo/hr_employee.xml',
        'demo/product_product.xml',
    ],
    "application": True,
    "installable": True,
    "auto-install": True,
}
