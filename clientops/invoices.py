"""Generate English PDF invoices from JSON input."""
from __future__ import annotations
import json
from datetime import date
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

def load_json(path):
    p=Path(path)
    if not p.is_file(): raise FileNotFoundError(f"JSON file not found: {p}")
    try: data=json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc: raise ValueError(f"Invalid JSON in {p}: {exc}") from exc
    if not isinstance(data,dict): raise ValueError("Expected a JSON object")
    return data

def _decimal(value,field):
    try: n=Decimal(str(value))
    except (InvalidOperation,TypeError,ValueError) as exc: raise ValueError(f"{field} must be numeric") from exc
    if not n.is_finite(): raise ValueError(f"{field} must be finite")
    return n

def invoice_total(invoice):
    items=invoice.get("items")
    if not isinstance(items,list) or not items: raise ValueError("invoice.items must be a non-empty list")
    total=Decimal("0")
    for i,item in enumerate(items):
        if not isinstance(item,dict) or not str(item.get("description","")).strip(): raise ValueError(f"items[{i}].description is required")
        qty=_decimal(item.get("quantity"),f"items[{i}].quantity"); price=_decimal(item.get("unit_price"),f"items[{i}].unit_price")
        if qty<=0: raise ValueError("Quantity must be greater than zero")
        if price<0: raise ValueError("Unit price cannot be negative")
        total += qty*price
    return total.quantize(Decimal("0.01"),rounding=ROUND_HALF_UP)

def create_invoice_pdf(invoice_path,output_path,rates_path=None):
    data=load_json(invoice_path)
    for key in ("invoice_number","issue_date","due_date","currency"):
        if not str(data.get(key,"")).strip(): raise ValueError(f"Missing invoice field: {key}")
    for key in ("issue_date","due_date"): date.fromisoformat(str(data[key]))
    sender=data.get("from",{}); client=data.get("bill_to",{})
    if not isinstance(sender,dict) or not isinstance(client,dict): raise ValueError("from and bill_to must be objects")
    total=invoice_total(data); currency=str(data["currency"]).upper()
    if len(currency)!=3 or not currency.isalpha() or not currency.isupper(): raise ValueError("currency must be a 3-letter code")
    conversion=None
    if rates_path:
        rates_data=load_json(rates_path); base=str(rates_data.get("base_currency","")).upper()
        rates=rates_data.get("rates")
        if not isinstance(rates,dict) or currency not in rates: raise ValueError(f"No manual exchange rate found for {currency}")
        rate=_decimal(rates[currency],"exchange rate")
        if rate<=0: raise ValueError("Exchange rate must be greater than zero")
        rate_date=str(rates_data.get("updated_on","not specified"))
        if rate_date!="not specified": date.fromisoformat(rate_date)
        conversion=(base,rate,rate_date,(total*rate).quantize(Decimal("0.01"),rounding=ROUND_HALF_UP))
    out=Path(output_path); out.parent.mkdir(parents=True,exist_ok=True)
    styles=getSampleStyleSheet()
    story=[Paragraph("INVOICE",styles["Title"]),Paragraph(f"Invoice: {escape(str(data['invoice_number']))} | Issue: {escape(str(data['issue_date']))} | Due: {escape(str(data['due_date']))}",styles["Normal"]),Spacer(1,8*mm)]
    parties=[[Paragraph("<b>FROM</b><br/>"+escape(str(sender.get("name","")))+"<br/>"+escape(str(sender.get("email",""))),styles["Normal"]),Paragraph("<b>BILL TO</b><br/>"+escape(str(client.get("name","")))+"<br/>"+escape(str(client.get("email",""))),styles["Normal"])]]
    story.append(Table(parties,colWidths=[82*mm,82*mm])); story.append(Spacer(1,10*mm))
    rows=[["Description","Qty","Unit price","Amount"]]
    for item in data["items"]:
        q=_decimal(item["quantity"],"quantity"); p=_decimal(item["unit_price"],"unit_price")
        rows.append([str(item["description"]),str(q),f"{currency} {p:,.2f}",f"{currency} {q*p:,.2f}"])
    rows.append(["","", "TOTAL",f"{currency} {total:,.2f}"])
    table=Table(rows,colWidths=[82*mm,18*mm,35*mm,35*mm],repeatRows=1)
    table.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#e8edf4")),("GRID",(0,0),(-1,-1),0.4,colors.grey),("ALIGN",(1,1),(-1,-1),"RIGHT"),("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("FONTNAME",(2,-1),(-1,-1),"Helvetica-Bold"),("TOPPADDING",(0,0),(-1,-1),7),("BOTTOMPADDING",(0,0),(-1,-1),7)]))
    story.append(table)
    if conversion:
        base,rate,rate_date,converted=conversion
        story.extend([Spacer(1,5*mm),Paragraph(f"Indicative equivalent: {base} {converted:,.2f}",styles["Normal"]),Paragraph(f"Manual rate: 1 {currency} = {rate} {base} (updated {escape(rate_date)})",styles["Normal"])])
    if data.get("notes"): story.extend([Spacer(1,8*mm),Paragraph("NOTES",styles["Heading3"]),Paragraph(escape(str(data["notes"])),styles["Normal"])])
    SimpleDocTemplate(str(out),pagesize=A4,rightMargin=20*mm,leftMargin=20*mm,topMargin=18*mm,bottomMargin=18*mm).build(story)
    return out
