"""Command-line interface."""
import argparse
import sys
from pathlib import Path
from .analyzer import load_products, write_ranked_csv, write_summary


def main() -> None:
    parser = argparse.ArgumentParser(prog="oprt", description="Open Product Research Toolkit")
    sub = parser.add_subparsers(dest="command", required=True)
    validate = sub.add_parser("validate", help="validate a product CSV")
    validate.add_argument("csv_file")
    analyze = sub.add_parser("analyze", help="rank products and export reports")
    analyze.add_argument("csv_file")
    analyze.add_argument("--out", default="reports", help="output directory (default: reports)")
    args = parser.parse_args()
    try:
        products = load_products(args.csv_file)
        if args.command == "validate":
            print(f"OK: validated {len(products)} product rows.")
            return
        out = Path(args.out)
        write_ranked_csv(products, out / "ranked_products.csv")
        write_summary(products, out / "summary.md")
        print(f"Analyzed {len(products)} products.")
        print(f"CSV report: {out / 'ranked_products.csv'}")
        print(f"Summary:    {out / 'summary.md'}")
    except (ValueError, FileNotFoundError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(2)
