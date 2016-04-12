# -*- coding: utf-8 -*-
# © <2016> <Jarsa Sistemas, S.A. de C.V.>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.exceptions import UserError
from openerp.tests.common import TransactionCase


class TestTmsRoute(TransactionCase):
    """
    This will test model tms_place
    """

    def setUp(self):
        """
        Define global variables
        """
        super(TestTmsRoute, self).setUp()
        self.route = self.env.ref('tms.tms_route_01')

    def test_10_tms_route_get_route_info(self):
        '''
        This test check that method get route info works.
        '''
        self.route.get_route_info()
        self.assertEqual(self.route.travel_time, float('8.1206'),
                         'Travel time is not correct')
        self.assertAlmostEqual(self.route.distance, float('946.8810'),
                               msg='Distance is not correct')

    def test_20_tms_route_get_route_info_no_coords_arrival(self):
        '''
        This test check that if the arrival_id has coordinates.
        '''
        self.route.arrival_id.write({'latitude': False, 'longitude': False})
        with self.assertRaisesRegexp(
                UserError,
                "The arrival don't have coordinates."):
            self.route.get_route_info()

    def test_30_tms_route_get_route_info_no_coords_departure(self):
        '''
        This test check that if the departure_id has coordinates.
        '''
        self.route.departure_id.write({'latitude': False, 'longitude': False})
        with self.assertRaisesRegexp(
                UserError,
                "The departure don't have coordinates."):
            self.route.get_route_info()

    def test_40_tms_route_open_in_google(self):
        '''
        This test check that method open in google works.
        '''
        self.route.open_in_google()
