# ClientOps Kit

An open-source, local-first starter toolkit for freelancers working with international clients.

**Status: early prototype (v0.1.0).** It uses sample data, has no hosted service, no users, and no production integrations.

## Features
- Generate English PDF invoices from JSON.
- Calculate invoice totals and optionally show conversions using manually supplied exchange rates.
- Create weekly Markdown activity reports from Git commit subjects.
- Draft polite or firm English payment reminders; emails are never sent automatically.

## Requirements
- Python 3.10+
- Git (for weekly activity reports)

## Install
```bash
python -m venv .venv
# macOS/Linux: source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -e .
```

## Examples
```bash
clientops invoice --input examples/invoice.sample.json --output output/invoice.pdf
clientops invoice --input examples/invoice.sample.json --rates examples/exchange-rates.sample.json --output output/invoice.pdf
clientops report --repo . --since 2026-11-16 --until 2026-11-22 --output output/weekly-report.md
clientops reminder --input examples/invoice.sample.json --tone polite --as-of 2026-11-22 --output output/reminder.txt
```

Exchange-rate values in the sample file are placeholders. Verify and update them before using conversions. The Git report reflects commit subjects only and cannot verify task completion. Review all invoice and reminder content before sending it to a client.

## Tests
```bash
python -m unittest discover -s tests -v
```

## Privacy
Use anonymized or sample client data in public demos. Never commit real client information, invoice PDFs, credentials, API keys, or private project details.

## License
MIT