# -*- coding: utf-8 -*-
# Copyright 2017, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import exceptions
from odoo.tests.common import TransactionCase


class TestFleetVehicleLogFuel(TransactionCase):

    def setUp(self):
        super(TestFleetVehicleLogFuel, self).setUp()
        self.log_fuel = self.env['fleet.vehicle.log.fuel']
        self.fuel_log = self.env.ref('tms.tms_fuel_log_01')
        self.fuel_log2 = self.env.ref('tms.tms_fuel_log_02')
        self.operating_unit = self.env.ref(
            'operating_unit.main_operating_unit')

    def create_log_fuel(self):
        self.log_fuel.create({
            "operating_unit_id": self.operating_unit.id,
            "vendor_id": self.env.ref("base.res_partner_1").id,
            "travel_id": self.env.ref("tms.tms_travel_01").id,
            "vehicle_id": self.env.ref("tms.tms_fleet_vehicle_01").id,
            "product_id": self.env.ref("tms.product_fuel").id,
            "product_qty": 1773.001,
            "tax_amount": 4053.34,
            "price_total": 29945.98,
            "ticket_number": 1234,
        })

    def test_10_fleet_vehicle_log_fuel(self):
        self.fuel_log.price_subtotal = 100
        self.fuel_log.product_qty = 10
        price = self.fuel_log.price_unit
        self.assertEqual(price, 10)

        self.fuel_log.price_subtotal = 0
        self.fuel_log.product_qty = 0
        price = self.fuel_log.price_unit
        self.assertEqual(price, 0)

    def test_20_fleet_vehicle_log_fuel_create(self):
        self.operating_unit.fuel_log_sequence_id = False
        with self.assertRaises(
                exceptions.ValidationError):
            self.create_log_fuel()
