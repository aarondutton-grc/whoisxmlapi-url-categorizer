# WhoisXML URL Categorizer

A Python command-line tool that scans one or more URLs for content categorization using the [WhoisXML Website Categorization API](https://website-categorization.whoisxmlapi.com/). Results include general content categories and IAB taxonomy classifications with confidence scores.

---

## Skills Demonstrated

- REST API integration with query parameter authentication
- `.env`-based API key management using `python-dotenv`
- Batch input processing from file (`-f urls.txt`) with rate limiting
- Argparse CLI design with multiple input modes (interactive, single, batch, JSON)
- Structured error handling for HTTP errors, timeouts, and connection failures
- IAB content taxonomy parsing and formatted terminal output

---

## Features

- **Single URL** scan via command-line argument
- **Batch scan** from a plain text file (one URL per line)
- **Interactive mode** — prompts for URLs if none are provided
- **JSON output** flag for piping or downstream processing
- **Rate limiting** — 1-second delay between batch requests to avoid API throttling
- **Auto-prefixing** — bare domains (without `https://`) are handled automatically
- Confidence scores displayed as percentages for both general and IAB categories

---

## Requirements

```
requests
python-dotenv
```

Install with:

```bash
pip install requests python-dotenv
```

---

## Setup

1. Sign up for a free account at [website-categorization.whoisxmlapi.com](https://website-categorization.whoisxmlapi.com/)
2. Copy your API key from the dashboard
3. Create a `.env` file in the project directory:

```
WHOISXML_API_KEY=your_key_here
```

> **Note:** Free trial credits are limited and do not renew. Monitor your remaining credits at [user.whoisxmlapi.com/products](https://user.whoisxmlapi.com/products). Once exhausted, a paid plan or additional credit purchase is required.

---

## Usage

```bash
# Interactive prompt
python url_categorizer.py

# Single URL
python url_categorizer.py https://example.com

# Multiple URLs as arguments
python url_categorizer.py https://example.com https://google.com

# Batch from file (one URL per line)
python url_categorizer.py -f urls.txt

# Raw JSON output
python url_categorizer.py https://example.com --json
```

### urls.txt format

```
https://example.com
https://google.com
https://github.com
```

One URL per line, no commas or quotes. Blank lines are ignored.

---

## Example Output

```
Scanning 1 URL(s) — 2026-05-09 09:01:21

Results
============================================================
------------------------------------------------------------
[1] URL     : https://cnn.com
    Domain  : https://cnn.com
    General Categories (8):
      • Business and Finance  Confidence: 96.0%
      • Media Industry  Confidence: 93.0%
      • News and Politics  Confidence: 96.0%
      • Politics  Confidence: 91.0%
      • National News  Confidence: 90.0%
      • International News  Confidence: 93.0%
      • Sports  Confidence: 92.0%
      • Television  Confidence: 94.0%
============================================================
Summary: 1 categorized | 0 no result | 0 error(s)
```

---

## GRC / Security Use Cases

This tool supports content-based risk assessment workflows relevant to third-party and vendor risk management:

- **Vendor risk intake** — verify that a vendor's primary domain categorizes as expected (e.g., healthcare, finance, SaaS) before initiating a full assessment
- **Third-party monitoring** — flag unexpected category shifts (e.g., a known vendor domain suddenly categorizing as gambling or adult content may indicate domain hijacking or compromise)
- **Acceptable use policy enforcement** — batch-scan URLs from proxy/firewall logs to identify categories that violate AUP, such as social media, gaming, or streaming on corporate networks
- **Phishing triage** — quickly categorize suspicious URLs reported by users to determine whether they represent known-bad categories before deeper analysis

---

## API Reference

- **Endpoint:** `https://website-categorization.whoisxmlapi.com/api/v3`
- **Auth:** API key passed as query parameter (`apiKey`)
- **Response fields used:** `categories`, `iabCategories`, `domainName`
- **Taxonomy:** Results follow the [IAB Content Taxonomy](https://www.iab.com/guidelines/content-taxonomy/)

---

## Author

Aaron Dutton  
License: MIT
