# Copyright 2017 Tecnativa - David Vidal
# Copyright 2017 Tecnativa - Luis M. Ontalba
# Copyright 2019 Tecnativa - Carlos Dauden
# Copyright 2026 ZerEVer
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common, tagged

NORMAL_REPORT = "stock.action_report_delivery"
VALUED_REPORT = "stock_picking_report_valued_print.action_report_delivery_valued"


@tagged("post_install", "-at_install")
class TestStockPickingReportValuedPrint(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        company = cls.env.user.company_id
        cls.tax = cls.env["account.tax"].create(
            {
                "name": "TAX 15%",
                "amount_type": "percent",
                "type_tax_use": "sale",
                "amount": 15.0,
            }
        )
        cls.tax10 = cls.env["account.tax"].create(
            {
                "name": "TAX 10%",
                "amount_type": "percent",
                "type_tax_use": "sale",
                "amount": 10.0,
            }
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test stuff",
                "list_price": 100.0,
                "taxes_id": [(6, 0, cls.tax.ids)],
            }
        )
        cls.partner = cls.env["res.partner"].create({"name": "Mr. Odoo"})
        line_vals = {
            "product_id": cls.product.id,
            "price_unit": 100,
            "product_uom_qty": 1,
        }
        cls.sale_order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "order_line": [(0, 0, dict(line_vals))],
                "company_id": company.id,
            }
        )
        cls.sale_order2 = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "order_line": [
                    (0, 0, dict(line_vals)),
                    (0, 0, dict(line_vals)),
                    (0, 0, dict(line_vals, tax_id=[(6, 0, cls.tax10.ids)])),
                ],
                "company_id": company.id,
            }
        )
        company.tax_calculation_rounding_method = "round_per_line"

    def _get_done_picking(self):
        self.sale_order.action_confirm()
        picking = self.sale_order.picking_ids
        picking.action_assign()
        for move in picking.move_ids:
            move.quantity_done = move.product_uom_qty
        picking._action_done()
        self.assertEqual(picking.state, "done")
        return picking

    def _render(self, report_ref, picking):
        html, _fmt = self.env["ir.actions.report"]._render_qweb_html(
            report_ref, picking.ids
        )
        return html.decode()

    # Amounts (same behaviour as OCA stock_picking_report_valued)

    def test_01_confirm_order(self):
        self.sale_order.action_confirm()
        self.assertTrue(len(self.sale_order.picking_ids))
        for picking in self.sale_order.picking_ids:
            picking.action_assign()
            self.assertEqual(picking.amount_untaxed, 100.0)
            self.assertEqual(picking.amount_tax, 15.0)
            self.assertEqual(picking.amount_total, 115.0)

    def test_02_not_reserved(self):
        """Valued picking isn't computed if not reserved"""
        self.sale_order.action_confirm()
        for picking in self.sale_order.picking_ids:
            picking.action_assign()
            picking.do_unreserve()
            self.assertEqual(picking.amount_untaxed, 0.0)
            self.assertEqual(picking.amount_tax, 0.0)
            self.assertEqual(picking.amount_total, 0.0)

    def test_03_tax_rounding_method(self):
        self.sale_order.company_id.tax_calculation_rounding_method = "round_globally"
        self.sale_order.action_confirm()
        self.assertTrue(len(self.sale_order.picking_ids))
        for picking in self.sale_order.picking_ids:
            picking.action_assign()
            self.assertEqual(picking.amount_untaxed, 100.0)
            self.assertEqual(picking.amount_tax, 15.0)
            self.assertEqual(picking.amount_total, 115.0)

    def test_04_lines_distinct_tax(self):
        self.sale_order2.company_id.tax_calculation_rounding_method = "round_globally"
        self.sale_order2.action_confirm()
        self.assertTrue(len(self.sale_order2.picking_ids))
        for picking in self.sale_order2.picking_ids:
            picking.action_assign()
            self.assertEqual(picking.amount_untaxed, 300.0)
            self.assertEqual(picking.amount_tax, 40.0)
            self.assertEqual(picking.amount_total, 340.0)

    def test_05_distinct_qty(self):
        self.sale_order.action_confirm()
        self.assertTrue(len(self.sale_order.picking_ids))
        for picking in self.sale_order.picking_ids:
            picking.action_assign()
            picking.move_line_ids.qty_done = 2.0
            self.assertEqual(picking.amount_untaxed, 200.0)
            self.assertEqual(picking.amount_tax, 30.0)
            self.assertEqual(picking.amount_total, 230.0)

    def test_06_report_total_block_not_shown_by_default(self):
        self.sale_order.action_confirm()
        picking = self.sale_order.picking_ids[0]
        picking.action_assign()
        self.assertFalse(picking._show_report_valued_total_block())

    # Print menu choice

    def test_10_valued_report_in_print_menu(self):
        report = self.env.ref(VALUED_REPORT)
        self.assertEqual(report.binding_model_id.model, "stock.picking")
        self.assertEqual(report.binding_type, "report")
        # The standard report is still there
        self.assertEqual(
            self.env.ref(NORMAL_REPORT).binding_model_id.model, "stock.picking"
        )

    def test_11_normal_report_not_valued(self):
        html = self._render(NORMAL_REPORT, self._get_done_picking())
        self.assertNotIn("th_sml_unit_price", html)
        self.assertNotIn("td_sml_subtotal", html)
        self.assertNotIn("valued_picking_amounts", html)
        self.assertIn("th_sml_qty_ordered", html)

    def test_12_valued_report_valued(self):
        html = self._render(VALUED_REPORT, self._get_done_picking())
        self.assertIn("th_sml_unit_price", html)
        self.assertIn("td_sml_subtotal", html)
        self.assertIn("valued_picking_amounts", html)
        self.assertNotIn("th_sml_qty_ordered", html)

    def test_13_valued_report_only_for_sale_deliveries(self):
        """A picking without sale order prints as the normal one"""
        picking_type = self.env.ref("stock.picking_type_out")
        picking = self.env["stock.picking"].create(
            {
                "partner_id": self.partner.id,
                "picking_type_id": picking_type.id,
                "location_id": picking_type.default_location_src_id.id,
                "location_dest_id": self.env.ref("stock.stock_location_customers").id,
                "move_ids": [
                    (
                        0,
                        0,
                        {
                            "name": self.product.name,
                            "product_id": self.product.id,
                            "product_uom": self.product.uom_id.id,
                            "product_uom_qty": 1,
                            "location_id": picking_type.default_location_src_id.id,
                            "location_dest_id": self.env.ref(
                                "stock.stock_location_customers"
                            ).id,
                        },
                    )
                ],
            }
        )
        picking.action_confirm()
        picking.action_assign()
        picking.move_ids.quantity_done = 1
        picking._action_done()
        html = self._render(VALUED_REPORT, picking)
        self.assertNotIn("th_sml_unit_price", html)
        self.assertNotIn("valued_picking_amounts", html)

    def test_14_oca_partner_flag_neutralized(self):
        """``valued`` (used by OCA stock_picking_report_valued) is always False,
        so the standard Delivery Slip is never valued by partner."""
        picking = self._get_done_picking()
        self.assertFalse(picking.valued)
        if "valued_picking" in self.partner._fields:
            self.partner.valued_picking = True
            picking.invalidate_recordset(["valued"])
            self.assertFalse(picking.valued)
            html = self._render(NORMAL_REPORT, picking)
            self.assertNotIn("th_sml_unit_price", html)
