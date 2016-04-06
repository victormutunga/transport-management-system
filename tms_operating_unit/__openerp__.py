# -*- coding: utf-8 -*-
# © 2016 Jarsa Sistemas, S.A. de C.V.
# - Jesús Alan Ramos Rodríguez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Operating Unit for TMS",
    "summary": "Adds functionality of use operating units in tms models",
    "version": "9.0.1.0.0",
    "category": "TMS",
    "website": "https://www.jarsa.com.mx/",
    "author": "Jarsa Sistemas, S.A. de C.V., Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": False,
    "depends": [
        "operating_unit",
    ],
    "data": [
        "views/operating_unit_view.xml",
        "data/ir_sequence.xml",
    ],
    "demo": [],
}
