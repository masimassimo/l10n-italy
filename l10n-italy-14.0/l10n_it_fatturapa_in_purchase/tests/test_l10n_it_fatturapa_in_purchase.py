#  Copyright 2019 Simone Rubino - Agile Business Group
#  License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime

from odoo.fields import first
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

from odoo.addons.l10n_it_fatturapa_in.tests.fatturapa_common import FatturapaCommon


class Testl10nItFatturapaInPurchase(FatturapaCommon):
    def setUp(self):
        super().setUp()
        order_model = self.env["purchase.order"]
        self.partner_id = self.env.ref("base.res_partner_1")
        self.product_id_1 = self.env.ref("product.product_product_8")
        self.order = order_model.create(
            {
                "name": "test_po",
                "partner_id": self.partner_id.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": self.product_id_1.name,
                            "product_id": self.product_id_1.id,
                            "product_qty": 5.0,
                            "product_uom": self.product_id_1.uom_po_id.id,
                            "price_unit": 500.0,
                            "date_planned": datetime.today().strftime(
                                DEFAULT_SERVER_DATETIME_FORMAT
                            ),
                        },
                    )
                ],
            }
        )

    def test_fatturapa_in_purchase(self):
        """Check that `name_get` works properly. verify to_invoice field"""
        res = self.run_wizard("test_fatturapa_in_purchase", "IT05979361218_008.xml")
        invoice_id = res.get("domain")[0][2][0]
        invoice = self.invoice_model.browse(invoice_id)

        inv_line = first(invoice.invoice_line_ids)
        order_line = first(self.order.order_line)
        inv_line.purchase_line_id = order_line

        self.assertEqual(order_line.display_name, "test_po: Large Desk")
        self.assertFalse(order_line.to_invoice)
        order_line.product_id.write({"purchase_method": "purchase"})
        self.order.button_approve()
        self.assertTrue(order_line.to_invoice)
