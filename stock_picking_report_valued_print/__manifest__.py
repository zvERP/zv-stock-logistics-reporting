# Copyright 2014 Pedro M. Baeza - Tecnativa <pedro.baeza@tecnativa.com>
# Copyright 2015 Antonio Espinosa - Tecnativa <antonio.espinosa@tecnativa.com>
# Copyright 2016-2019 Carlos Dauden - Tecnativa <carlos.dauden@tecnativa.com>
# Copyright 2017 David Vidal - Tecnativa <david.vidal@tecnativa.com>
# Copyright 2017 Luis M. Ontalba - Tecnativa <luis.martinez@tecnativa.com>
# Copyright 2026 ZerEVer
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
#
# Based on OCA/stock-logistics-reporting stock_picking_report_valued (16.0).
{
    "name": "Valued Delivery Slip (choose when printing)",
    "summary": "Adds a 'Delivery Slip (Valued)' entry to the Print menu, "
    "next to the standard Delivery Slip",
    "version": "16.0.1.0.0",
    "category": "Warehouse Management",
    "author": "ZerEVer",
    "license": "AGPL-3",
    "depends": ["sale_stock"],
    "data": ["report/report_deliveryslip_valued.xml"],
    "installable": True,
    "application": False,
}
