"""Command-line interface for ClientOps Kit."""
from __future__ import annotations
import argparse
import sys
from . import __version__
from .invoices import create_invoice_pdf
from .reports import write_weekly_report
from .reminders import write_reminder_draft

def build_parser():
    parser = argparse.ArgumentParser(prog="clientops", description="Local-first utilities for freelancers.")
    parser.add_argument("--version", action="version", version=f"ClientOps Kit {__version__}")
    commands = parser.add_subparsers(dest="command", required=True)
    invoice = commands.add_parser("invoice", help="Create an English PDF invoice")
    invoice.add_argument("--input", required=True)
    invoice.add_argument("--output", default="output/invoice.pdf")
    invoice.add_argument("--rates")
    report = commands.add_parser("report", help="Create a weekly Git activity report")
    report.add_argument("--repo", default=".")
    report.add_argument("--since", required=True)
    report.add_argument("--until", required=True)
    report.add_argument("--output", default="output/weekly-report.md")
    reminder = commands.add_parser("reminder", help="Create a payment reminder draft; does not send email")
    reminder.add_argument("--input", required=True)
    reminder.add_argument("--tone", choices=["polite", "firm"], default="polite")
    reminder.add_argument("--as-of")
    reminder.add_argument("--output", default="output/payment-reminder.txt")
    return parser

def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "invoice":
            output = create_invoice_pdf(args.input, args.output, args.rates)
        elif args.command == "report":
            output = write_weekly_report(args.repo, args.since, args.until, args.output)
        else:
            output = write_reminder_draft(args.input, args.output, args.tone, args.as_of)
    except (FileNotFoundError, ValueError, RuntimeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    print(f"Created: {output}")
    return 0
