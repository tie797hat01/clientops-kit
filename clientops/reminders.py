"""Create payment reminder drafts; this module never sends email."""
from datetime import date
from decimal import Decimal
from pathlib import Path
from .invoices import load_json, invoice_total

def create_reminder_draft(invoice_path,tone="polite",as_of=None):
    if tone not in {"polite","firm"}: raise ValueError("tone must be polite or firm")
    data=load_json(invoice_path); client=data.get("bill_to",{}); sender=data.get("from",{})
    due=date.fromisoformat(data["due_date"]); today=date.fromisoformat(as_of) if as_of else date.today()
    delta=(due-today).days; currency=str(data["currency"]).upper()
    amount=f"{currency} {invoice_total(data):,.2f}"
    timing=f"was due on {due.isoformat()} ({abs(delta)} day(s) ago)" if delta<0 else (f"is due today ({due.isoformat()})" if delta==0 else f"is due on {due.isoformat()} (in {delta} day(s))")
    if tone=="polite":
        request="Could you let me know when I can expect the payment?" if delta<0 else "Please let me know if you need any details before the due date."
    else:
        request="Please arrange payment or let me know the expected payment date." if delta<0 else "Please make sure payment is arranged by the due date."
    name=client.get("name","there"); sender_name=sender.get("name","[Your name]")
    body=f"Hi {name},\n\nI’m following up on invoice {data['invoice_number']} for {amount}, which {timing}.\n\n{request}\n\nThank you,\n{sender_name}"
    return f"To: {client.get('email','[client email]')}\nSubject: Payment reminder — Invoice {data['invoice_number']}\n\n{body}\n"

def write_reminder_draft(invoice_path,output_path,tone="polite",as_of=None):
    out=Path(output_path); out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(create_reminder_draft(invoice_path,tone,as_of),encoding="utf-8"); return out
