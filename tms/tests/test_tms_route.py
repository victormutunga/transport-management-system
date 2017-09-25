# -*- coding: utf-8 -*-
# Copyright 2016, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import simplejson as json

from mock import MagicMock

from odoo.exceptions import UserError, ValidationError
from odoo.tests.common import TransactionCase


class TestTmsRoute(TransactionCase):

    def setUp(self):
        super(TestTmsRoute, self).setUp()
        self.route = self.env.ref('tms.tms_route_01')
        self.vehicle = self.env.ref('tms.tms_fleet_vehicle_01')
        self.result = {
            'status': 'OK',
            'rows': [{
                'elements': [{
                    'duration': {'text': '8 hours 00 mins', 'value': 29506},
                    'distance': {'text': '950 km', 'value': 946887},
                    'status': 'OK'}]}],
            'origin_addresses': [
                '501-599 E Mills Ave, El Paso, TX 79901, USA'],
            'destination_addresses': [
                '206 N Guadalupe St, San Marcos, TX 78666, USA']}

    def test_10_tms_route_on_change_distance_empty(self):
        self.route.write({'distance_empty': 150.00})
        self.route.on_change_disance_empty()
        self.assertEqual(
            self.route.distance_loaded,
            737.00,
            'On change works')
        with self.assertRaises(ValidationError):
            self.route.update({'distance_empty': -10.0})
            self.route.on_change_disance_empty()

    def test_20_tms_route_on_change_distance_loaded(self):
        self.route.write({'distance_loaded': 150.00})
        self.route.on_change_disance_loaded()
        self.assertEqual(
            self.route.distance_empty,
            737.00,
            'On change works')
        with self.assertRaises(ValidationError):
            self.route.update({'distance_loaded': -10.0})
            self.route.on_change_disance_loaded()

    def test_30_tms_route_get_route_info(self):
        json.loads = MagicMock()
        json.loads.return_value = self.result
        self.route.get_route_info()
        self.assertEqual(self.route.travel_time, 8.196100000000001,
                         msg='Travel time is not correct')
        self.assertEqual(self.route.distance, 946.8870000000001,
                         msg='Distance is not correct')
        json.loads.return_value = False
        with self.assertRaisesRegexp(
                UserError,
                'Google Maps is not available.'):
            self.route.get_route_info()

    def test_40_tms_route_open_in_google(self):
        self.route.open_in_google()

    def test_50_tms_route_get_fuel_efficiency(self):
        self.route.get_fuel_efficiency(self.vehicle, 'double')
