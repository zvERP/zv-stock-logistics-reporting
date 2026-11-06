============================================
Valued Delivery Slip (choose when printing)
============================================

This module adds a second delivery slip to the *Print* menu of transfers:

* **Delivery Slip**: the standard Odoo report, never valued.
* **Delivery Slip (Valued)**: the same report with prices, discounts, taxes
  and totals taken from the related sale order lines.

The decision of printing a valued delivery slip or not is therefore taken at
print time, instead of being fixed per customer.

It is based on (and largely copied from) the OCA module
`stock_picking_report_valued
<https://github.com/OCA/stock-logistics-reporting/tree/16.0/stock_picking_report_valued>`_
by Tecnativa, but it does not depend on it.

Usage
=====

#. Create and confirm a sale order with products to deliver.
#. Open the delivery from the *Delivery* smart button.
#. Go to *Print* and choose *Delivery Slip* or *Delivery Slip (Valued)*.

As in the OCA module, amounts are only printed on outgoing transfers linked to
a sale order. If the transfer is done it is valued with the done quantity,
otherwise with the reserved quantity. Detailed lines are printed in the move
line table, which Odoo only shows for done transfers; for transfers not yet
done only the totals table is printed.

The valued report reuses the standard ``stock.report_deliveryslip`` template,
so any other customisation of the delivery slip also applies to it. Valued
blocks are only rendered when the QWeb variable ``print_valued`` is set.

Compatibility with OCA ``stock_picking_report_valued``
======================================================

Both modules can be installed at the same time. In that case this module
takes precedence and cancels the OCA behaviour:

* The ``valued`` field of transfers (``partner_id.valued_picking`` in the OCA
  module) is redefined to be always ``False``, so the standard Delivery Slip
  is never valued per customer. The *Valued picking* checkbox on partners is
  still visible but has no effect.
* Amount fields and methods (``amount_untaxed``, ``sale_price_subtotal``,
  ``_get_report_valued_total_amount``...) keep the OCA names, so they are
  shared instead of duplicated, and extensions written for the OCA module
  keep working on the valued report.

This relies on Odoo loading modules of the same dependency depth in
alphabetical order (``stock_picking_report_valued`` before
``stock_picking_report_valued_print``). Keep ``depends`` to ``sale_stock``
only so that both modules stay at the same depth.

Any other module that relies on ``o.valued`` in its templates is
neutralized as well.

Known limitations
=================

* If the transfer is not reserved, amounts are not computed.

Credits
=======

Based on ``stock_picking_report_valued`` (OCA), whose authors are Tecnativa
(Pedro M. Baeza, Antonio Espinosa, Carlos Dauden, David Vidal, Luis M.
Ontalba, Ernesto Tejeda, Sergio Teruel) and the other OCA contributors.
