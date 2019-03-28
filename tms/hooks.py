# -*- coding: utf-8 -*-
# Copyright 2019, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, SUPERUSER_ID

products = [
    'product.product_product_16',
    'product.product_product_24',
    'product.consu_delivery_01',
    'product.consu_delivery_02',
    'product.consu_delivery_03',
    'product.product_product_22',
    'product.product_product_4',
    'product.product_product_4b',
    'product.product_product_4c',
    'product.product_product_5b',
    'product.product_product_5',
    'product.product_product_6',
    'product.product_product_7',
    'product.product_product_8',
    'product.product_product_9',
    'product.product_product_10',
    'product.product_product_11',
    'product.product_product_11b',
    'product.product_product_17',
    'product.product_product_27',
    'product.product_product_25',
    'product.product_product_12',
    'product.product_product_20',
    'product.product_product_3',
    'product.product_delivery_01',
    'product.product_delivery_02',
    'product.product_order_01',
    'product.product_product_13',
    'product.service_cost_01',
    'product.service_delivery',
    'product.service_order_01',
    'product.product_product_1',
    'product.product_product_2',
    'product.product_product_7_product_template',
    'product.product_product_9_product_template',
    'product.consu_delivery_03_product_template',
    'product.membership_2_product_template',
    'product.product_product_5b_product_template',
    'product.product_product_16_product_template',
    'product.product_product_3_product_template',
    'product.service_delivery_product_template',
    'product.product_product_5_product_template',
    'product.product_delivery_02_product_template',
    'product.service_cost_01_product_template',
    'product.product_product_1_product_template',
    'product.membership_0_product_template',
    'product.product_product_24_product_template',
    'product.product_product_17_product_template',
    'product.product_product_27_product_template',
    'product.product_product_25_product_template',
    'product.consu_delivery_02_product_template',
    'product.product_product_20_product_template',
    'product.product_product_10_product_template',
    'product.product_product_12_product_template',
    'product.service_order_01_product_template',
    'product.product_product_22_product_template',
    'product.product_product_13_product_template',
    'product.consu_delivery_01_product_template',
    'product.membership_1_product_template',
    'product.product_product_2_product_template',
    'product.product_delivery_01_product_template',
    'product.product_order_01_product_template',
    'product.product_product_8_product_template',
    'product.product_product_6_product_template',
    'product.product_product_4_product_template',
    'product.product_product_11_product_template',
]


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    module = env.ref('base.module_tms')
    stock = env.ref('base.module_stock')
    if module.demo:
        env['fleet.vehicle.log.fuel'].search([]).unlink()
        env['fleet.vehicle.odometer'].search([]).unlink()
        if stock.state == 'installed':
            env['stock.warehouse.orderpoint'].search([]).unlink()
        for product in products:
            env.ref(product).write({'active': False})
