# -*- coding: utf-8 -*-
# © <2016> <Jarsa Sistemas, S.A. de C.V.>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.exceptions import UserError
from openerp.tests.common import TransactionCase


class TestTmsPlace(TransactionCase):
    """
    This will test model tms_place
    """

    def setUp(self):
        """
        Define global variables
        """
        super(TestTmsPlace, self).setUp()
        self.place = self.env.ref('tms.tms_place_01')

    def test_10_tms_place_get_coordinates(self):
        '''
        This test check that method get coords works.
        '''
        self.place.get_coordinates()
        self.assertEqual(self.place.latitude, float('29.4241219000'),
                         'Latitude is done')
        self.assertEqual(self.place.longitude, float('-98.4936282000'),
                         'Longitude is working')

    def test_20_tms_place_open_in_google(self):
        '''
        This test check that method open in google works.
        '''
        self.place.open_in_google()

    def test_30_tms_place_compute_complete_name(self):
        '''
        This test check the compute complete name works.
        '''
        self.place._compute_complete_name()
        self.assertEqual(self.place.complete_name, 'San Antonio, Texas',
                         'Full Complete Name')

    def test_40_tms_place_get_coordinates_force_error(self):
        '''
        This test check that Usererror get coords works.
        '''
        with self.assertRaisesRegexp(
                UserError,
                "Google Maps is not available."):
            self.place.get_coordinates(error=True)
