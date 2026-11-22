import json
import tempfile
import unittest
from pathlib import Path
from clientops.reminders import create_reminder_draft

SAMPLE={"invoice_number":"TEST-001","due_date":"2026-11-20","currency":"USD","from":{"name":"Freelancer"},"bill_to":{"name":"Sample Client","email":"client@example.com"},"items":[{"description":"Editing","quantity":2,"unit_price":50}]}

class ReminderTests(unittest.TestCase):
    def test_polite_draft_contains_amount(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"invoice.json"; p.write_text(json.dumps(SAMPLE))
            draft=create_reminder_draft(p,"polite","2026-11-22")
        self.assertIn("USD 100.00",draft)
        self.assertIn("2 day(s) ago",draft)
    def test_firm_tone(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"invoice.json"; p.write_text(json.dumps(SAMPLE))
            draft=create_reminder_draft(p,"firm","2026-11-22")
        self.assertIn("Please arrange payment",draft)

if __name__=="__main__": unittest.main()
