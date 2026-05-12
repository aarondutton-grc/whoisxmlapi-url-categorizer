"""
WHOISXML url categorizer.py
------------------
Scans one or more URLs for content categorization using the WhoisXML
Website Categorization API.

Free tier: 100 credits, no credit card required but note trial credits do not renew
once you use them all up you will receive an email asking you to buy more credits
or move to a paid plan
Sign up at: https://website-categorization.whoisxmlapi.com/

Set your API key in .env
    WHOISXML_API_KEY = your_key_here

Author: Aaron Dutton
License: MIT

requirements:
pip install requests python-dotenv
requirements.txt

config:
Sign up free at https://website-categorization.whoisxmlapi.com/
put WHOISXML_API_KEY in .env file
time.sleep(1) rate limiting between batch requests

Usage:
    python url_categorizer.py                         # interactive prompt
    python url_categorizer.py https://example.com     # single URL arg
    python url_categorizer.py https://a.com https://b.com # multiple URL args
    python url_categorizer.py -f urls.txt             # batch from file
    python url_categorizer.py https://example.com --json  # raw JSON output

Limits:
you can check limit credits at
https://user.whoisxmlapi.com/products
you only get 100 free credits on free trial then you have to buy credits...
"""

import sys
import os
import json
import argparse
import requests
import time  # add to imports at top
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

API_URL = "https://website-categorization.whoisxmlapi.com/api/v3"


def _get_api_key() -> str:
    return os.environ.get("WHOISXML_API_KEY", "YOUR_API_KEY_HERE")


# ---------------------------------------------------------------------------
# Core function
# ---------------------------------------------------------------------------

def categorize_url(url: str) -> dict:
    """
    Submit a URL to the WhoisXML Categorization API.
    Returns a dict with keys: url, categories, iab_categories, error.
    """
    params = {
        "apiKey": _get_api_key(),
        "url": url,
        "outputFormat": "JSON",
    }

    try:
        response = requests.get(API_URL, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()

        # WhoisXML returns 'categories' (general) and 'iabCategories' (IAB taxonomy)
        categories     = data.get("categories", [])
        iab_categories = data.get("iabCategories", [])

        return {
            "url": url,
            "domain": data.get("domainName", url),
            "categories": categories,
            "iab_categories": iab_categories,
            "error": None,
        }

    except requests.exceptions.HTTPError as e:
        status = e.response.status_code if e.response else "?"
        body = e.response.text[:300] if e.response else str(e)
        return {"url": url, "domain": url, "categories": [], "iab_categories": [], "error": f"HTTP {status}: {body}"}

    except requests.exceptions.ConnectionError:
        return {"url": url, "domain": url, "categories": [], "iab_categories": [], "error": "Connection error — check your internet."}

    except requests.exceptions.Timeout:
        return {"url": url, "domain": url, "categories": [], "iab_categories": [], "error": "Request timed out after 15 seconds."}

    except Exception as e:
        return {"url": url, "domain": url, "categories": [], "iab_categories": [], "error": str(e)}


# ---------------------------------------------------------------------------
# Display helper
# ---------------------------------------------------------------------------

def print_result(result: dict, index: int = None) -> None:
    prefix = f"[{index}] " if index is not None else ""
    sep = "-" * 60

    print(sep)
    print(f"{prefix}URL     : {result['url']}")
    print(f"    Domain  : {result['domain']}")

    if result["error"]:
        print(f"    ERROR   : {result['error']}")
        return

    cats = result.get("categories", [])
    iab  = result.get("iab_categories", [])

    if not cats and not iab:
        print("    RESULT  : No categories returned (domain may be unrecognized).")
    else:
        if cats:
            print(f"    General Categories ({len(cats)}):")
            for cat in cats:
                name       = cat.get("name", "Unknown")
                confidence = cat.get("confidence", "")
                conf_str   = f"  Confidence: {confidence:.1%}" if isinstance(confidence, float) else ""
                print(f"      • {name}{conf_str}")

        if iab:
            print(f"    IAB Categories ({len(iab)}):")
            for cat in iab:
                name       = cat.get("name", "Unknown")
                tier1      = cat.get("tier1", {}).get("name", "")
                confidence = cat.get("confidence", "")
                conf_str   = f"  Confidence: {confidence:.1%}" if isinstance(confidence, float) else ""
                tier_str   = f"  [{tier1}]" if tier1 else ""
                print(f"      • {name}{tier_str}{conf_str}")

    print()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Scan URLs for content categorization using the WhoisXML API."
    )
    parser.add_argument("urls", nargs="*", help="One or more URLs to categorize.")
    parser.add_argument("-f", "--file", metavar="FILE", help="Text file with one URL per line.")
    parser.add_argument("--json", action="store_true", help="Output raw JSON to stdout.")
    args = parser.parse_args()

    # --- Validate API key ---
    if _get_api_key() == "YOUR_API_KEY_HERE":
        print(
            "\n⚠  No API key detected.\n"
            "   1. Sign up free at https://website-categorization.whoisxmlapi.com/\n"
            "   2. Copy your API key from the dashboard\n"
            "   3. In PyCharm: Run > Edit Configurations > Environment Variables\n"
            "      Add:  WHOISXML_API_KEY = your_key_here\n"
        )
        sys.exit(1)

    # --- Collect URLs ---
    urls = list(args.urls)

    if args.file:
        try:
            with open(args.file, "r") as fh:
                urls.extend(line.strip() for line in fh if line.strip())
            #print(f"DEBUG — URLs loaded: {urls}")
        except FileNotFoundError:
            print(f"Error: File not found — {args.file}")
            sys.exit(1)

    if not urls:
        print("URL Categorizer — WhoisXML API")
        print("Enter URLs to scan (one per line). Press Enter on a blank line to start.\n")
        while True:
            entry = input("  URL: ").strip()
            if not entry:
                break
            urls.append(entry)

    if not urls:
        print("No URLs provided. Exiting.")
        sys.exit(0)

    # --- Run scans ---
    print(f"\nScanning {len(urls)} URL(s) — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    results = []

    for i, url in enumerate(urls, start=1):
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        print(f"  Querying [{i}/{len(urls)}]: {url} ...", end="\r")
        result = categorize_url(url)
        results.append(result)
        print(" " * 70, end="\r")
        time.sleep(1)

        # --- Output ---
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(f"\nResults\n{'=' * 60}")
        for i, result in enumerate(results, start=1):
            print_result(result, index=i)

        success = sum(1 for r in results if not r["error"] and (r["categories"] or r["iab_categories"]))
        no_cat  = sum(1 for r in results if not r["error"] and not r["categories"] and not r["iab_categories"])
        errors  = sum(1 for r in results if r["error"])

        print("=" * 60)
        print(f"Summary: {success} categorized | {no_cat} no result | {errors} error(s)")
        print()


if __name__ == "__main__":
    main()
