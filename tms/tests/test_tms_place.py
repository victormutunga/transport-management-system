# -*- coding: utf-8 -*-
# © <2016> <Jarsa Sistemas, S.A. de C.V.>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase
from openerp import api
from mock import MagicMock
from openerp.exceptions import UserError


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

    @api.depends('name', 'state_id')
    def test_40_tms_place_compute_complete_name(self):
        '''
        This test check the compute complete name.
        '''
        self.place.write({'name': 'San Francisco'})
        self.place._compute_complete_name()
        self.assertEqual(
            self.place.complete_name,
            'San Francisco, Texas',
            'On change works')
        self.place.write({'state_id': False})
        self.place._compute_complete_name()
        self.assertEqual(
            self.place.complete_name,
            'San Francisco',
            'On change works')

    def test_50_tms_place_get_cordinates(self):
        self.place.get_coordinates = MagicMock()
        self.place.get_coordinates.return_value = UserError(
            'Google Maps is not available.')
