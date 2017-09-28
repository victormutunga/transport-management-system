# -*- coding: utf-8 -*-
# Copyright 2017, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestHrEmployee(TransactionCase):

    def setUp(self):
        super(TestHrEmployee, self).setUp()
        self.employee_id = self.env.ref('tms.tms_hr_employee_01')

    def test_10_compute_days_to_expire(self):
        self.employee_id.update({
            'license_expiration': False,
            'days_to_expire': False,
        })
        self.assertEqual(self.employee_id.days_to_expire, 0)

    def test_20_get_driver_license_info(self):
        self.employee_id.get_driver_license_info()
        self.employee_id.driver_license = "Test"
        with self.assertRaisesRegexp(
                ValidationError,
                'The driver license is not in SCT database'):
            self.employee_id.get_driver_license_info()
