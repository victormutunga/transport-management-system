# -*- coding: utf-8 -*-
# © <2012> <Israel Cruz Argil, Argil Consulting>
# © <2016> <Jarsa Sistemas, S.A. de C.V.>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import time

from openerp import fields, models
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT


class TmsFactorSpecial(models.Model):
    _name = "tms.factor.special"
    _description = ("Python Code calculate Payment "
                    "(Driver/Supplier) &  Client charge")

    name = fields.Char('Special Name', size=200, required=True)
    active = fields.Boolean('Active', default=True)
    date = fields.Date('Date', required=True,
                       default=time.strftime(DEFAULT_SERVER_DATE_FORMAT))
    description = fields.Text('Description')
    python_code = fields.Text('Python Code', required=True)
    factor_ids = fields.One2many('tms.factor', 'factor_special_id', 'Factor')
    type = fields.Selection([
        ('salary', 'Driver Salary'),
        ('salary_distribution', 'Salary Distribution'),
        ('retention', 'Salary Retentions & Discounts'),
        ('supplier', 'Supplier Payment'), ], 'Type', required=True, help="""
Driver Salary => Use this for special Driver Salary calculation
Salary Distribution => Useful in some countries, you can make a Wage
distribution on several expenses, so Salary is masked for Tax purposes
Salary Retentions & Discounts => Use this for Driver Tax retentions
Supplier => Use this to calculate Supplier Travel Payment
                """)
