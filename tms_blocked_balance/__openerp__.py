# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2014 Argil Consulting - http://www.argil.mx
############################################################################
#    Coded by: German Ponce Dominguez (german.ponce@argil.mx)

{
    "name": "TMS - Bloqueo de Importes",
    "version": "1.0",
    "author": "Argil Consulting",
    "category": "TMS",
    "description" : """
TMS - Bloqueo de Importes
=========================

Este modulo bloquea  las facturas que provengan de órdenes de mantenimiento y almacén para no modificar los Importes.

1. Este Modulo Crea un Grupo Llamado TMS / Manager Contable, este grupo permite editar un CheckBox llamado Bloquear Importes,
este campo es el encargado de no permitir editar los Importes, si se desactiva entonces podras realizarlo.

2. Por Defecto en este Grupo Solo se encuentra el Administrador.

    """,
    "website": "http://www.argil.mx/",
    "license": "AGPL-3",
    "depends": [
            "account",
            "tms",
            "tms_maintenance",
                ],
    "demo": [],
    "data": [
            "views/tms_view.xml",
    ],
    "installable": False,
    "active": False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: