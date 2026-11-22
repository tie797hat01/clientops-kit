import unittest
from clientops.invoices import invoice_total

class InvoiceTests(unittest.TestCase):
    def test_invoice_total(self):
        data={"items":[{"description":"Writing","quantity":2,"unit_price":25.25},{"description":"Editing","quantity":1,"unit_price":10}]}
        self.assertEqual(str(invoice_total(data)),"60.50")
    def test_rejects_zero_quantity(self):
        with self.assertRaises(ValueError):
            invoice_total({"items":[{"description":"Work","quantity":0,"unit_price":10}]})

if __name__=="__main__": unittest.main()
