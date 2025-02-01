#!/usr/bin/env python3
"""
Reverse Whois Query Script with Extended Options

This independent tool allows you to query the Big Domain Data Reverse WHOIS API.
You can query either the 'current' or 'historical' database and filter results using various search fields.

Valid search fields include:
  domain_keyword, domain_name, domain_tld, query_date, query_date_from, query_date_to,
  query_year, create_date, create_date_from, create_date_to, create_year, update_date,
  update_date_from, update_date_to, update_year, expiry_date, expiry_date_from, expiry_date_to,
  expiry_year, registrar_iana, registrar_name, registrar_website, registrant_name,
  registrant_company, registrant_address, registrant_city, registrant_state, registrant_zip,
  registrant_country, registrant_email, registrant_phone, registrant_fax, name_servers,
  domain_status, dns_sec, and their respective wildcard versions (e.g. domain_keyword_wildcard).

Additional Options:
  --output <filename>  Specify a custom CSV output filename (overrides default naming).
  --show               Display the CSV output on the terminal.
  --balance            Check API balance only (skips reverse WHOIS query).
  --debug              Show debug logging information.

For more information on the API, please refer to:
https://www.bigdomaindata.com/guide.php
"""

import argparse
import csv
import datetime
import logging
import os
import sys
import requests

# ------------------------------------------------------------------------------
# Preliminary parsing to capture the --debug flag.
# This prevents --debug from being treated as an invalid query field.
# ------------------------------------------------------------------------------
prelim_parser = argparse.ArgumentParser(add_help=False)
prelim_parser.add_argument("--debug", action="store_true", help="Show debug logging information.")
prelim_args, remaining_args = prelim_parser.parse_known_args()

# Set logging level based on the --debug flag.
if prelim_args.debug:
    LOG_LEVEL = logging.DEBUG
else:
    LOG_LEVEL = logging.INFO

logging.basicConfig(
    level=LOG_LEVEL,  # Use DEBUG if --debug is passed, otherwise INFO.
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# ------------------------------------------------------------------------------
# Attempt to import the settings module to load the API key.
# ------------------------------------------------------------------------------
try:
    import settings
except ImportError:
    print("Error: settings.py file not found. Please create a settings.py with your API_KEY variable.")
    sys.exit(1)

if not hasattr(settings, "API_KEY") or not settings.API_KEY:
    print("Error: API_KEY not found or is empty in settings.py. Please add your API key and try again.")
    sys.exit(1)

# ------------------------------------------------------------------------------
# List of valid search fields.
# ------------------------------------------------------------------------------
VALID_SEARCH_FIELDS = [
    "domain_keyword",
    "domain_name",
    "domain_tld",
    "query_date",
    "query_date_from",
    "query_date_to",
    "query_year",
    "create_date",
    "create_date_from",
    "create_date_to",
    "create_year",
    "update_date",
    "update_date_from",
    "update_date_to",
    "update_year",
    "expiry_date",
    "expiry_date_from",
    "expiry_date_to",
    "expiry_year",
    "registrar_iana",
    "registrar_name",
    "registrar_website",
    "registrant_name",
    "registrant_company",
    "registrant_address",
    "registrant_city",
    "registrant_state",
    "registrant_zip",
    "registrant_country",
    "registrant_email",
    "registrant_phone",
    "registrant_fax",
    "name_servers",
    "domain_status",
    "dns_sec",
    # Wildcard search fields:
    "domain_name_wildcard",
    "domain_keyword_wildcard",
    "domain_tld_wildcard",
    "registrar_name_wildcard",
    "registrar_website_wildcard",
    "registrant_name_wildcard",
    "registrant_company_wildcard",
    "registrant_address_wildcard",
    "registrant_city_wildcard",
    "registrant_state_wildcard",
    "registrant_zip_wildcard",
    "registrant_email_wildcard",
    "registrant_phone_wildcard",
    "registrant_fax_wildcard",
    "name_servers_wildcard",
    "domain_status_wildcard",
    "dns_sec_wildcard"
]

# ------------------------------------------------------------------------------
def query_api(database, api_key, search_params):
    """
    Query the reverse WHOIS API using the specified database and search parameters.
    
    Each search field is added as its own parameter. For example:
      /?key=XXXXX&database=current&domain_keyword_wildcard=yahoo*&domain_tld=com&create_year=2000
    """
    base_url = "https://api.bigdomaindata.com/"
    params = {
        "key": api_key,
        "database": database,
    }
    params.update(search_params)
    
    logging.debug("Querying API with parameters: %s", {k: v for k, v in params.items() if k != "key"})
    try:
        response = requests.get(base_url, params=params)
        logging.debug("Received HTTP status code: %s", response.status_code)
        response.raise_for_status()
        json_response = response.json()
        logging.debug("API response JSON: %s", json_response)
        return json_response
    except requests.exceptions.RequestException as req_err:
        logging.error("Error during API request: %s", req_err, exc_info=True)
        raise

# ------------------------------------------------------------------------------
def check_api_balance(api_key):
    """
    Check the API balance.
    """
    base_url = "https://api.bigdomaindata.com/"
    params = {"key": api_key}
    logging.debug("Checking API balance.")
    try:
        response = requests.get(base_url, params=params)
        logging.debug("Balance query HTTP status code: %s", response.status_code)
        response.raise_for_status()
        balance_data = response.json()
        logging.debug("Balance API response JSON: %s", balance_data)
        return balance_data
    except requests.exceptions.RequestException as req_err:
        logging.error("Error during balance check: %s", req_err, exc_info=True)
        raise

# ------------------------------------------------------------------------------
def write_csv(results_data, output_filename=None):
    """
    Write the query results (from the "results" field) to a CSV file.
    The file is saved in a subfolder called "results" with the filename either:
      - reverse_whois_YYYY-MM-DD_HH:mm:ss.csv (default), or
      - the user-specified filename from --output.
    """
    results_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
    os.makedirs(results_dir, exist_ok=True)

    if output_filename:
        filename = output_filename
        if not filename.lower().endswith(".csv"):
            filename += ".csv"
    else:
        now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"reverse_whois_{now}.csv"

    filepath = os.path.join(results_dir, filename)
    logging.info("Saving CSV to: %s", filepath)

    all_keys = set()
    for result in results_data:
        all_keys.update(result.keys())
    all_keys = sorted(list(all_keys))

    processed_results = []
    for result in results_data:
        processed_row = {}
        for key in all_keys:
            value = result.get(key, "")
            if isinstance(value, list):
                value = ";".join(str(item) for item in value)
            processed_row[key] = value
        processed_results.append(processed_row)

    try:
        with open(filepath, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=all_keys)
            writer.writeheader()
            writer.writerows(processed_results)
        logging.info("CSV file saved successfully.")
    except Exception as e:
        logging.error("Error writing CSV file: %s", e, exc_info=True)
        raise

    return filepath

# ------------------------------------------------------------------------------
def main():
    """
    Main function to parse arguments, perform actions based on user input,
    and handle CSV output.
    """
    logging.info("Starting Reverse Whois Query Script.")

    results_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)
        logging.debug("Created results folder at: %s", results_dir)
    
    # Set up the main argument parser.
    parser = argparse.ArgumentParser(
        description=(
            "Reverse WHOIS Query Tool for the Big Domain Data Reverse WHOIS API.\n"
            "This independent tool allows you to query either the 'current' or 'historical' database.\n"
            "You can filter your query by providing one or more search field options.\n"
            "Valid search fields include:\n  " + ", ".join(VALID_SEARCH_FIELDS)
        ),
        epilog="For more information on the API, please refer to: https://www.bigdomaindata.com/guide.php"
    )
    # Add --debug so that it appears in help; its value defaults from prelim_args.
    parser.add_argument("--debug", action="store_true", default=prelim_args.debug,
                        help="Show debug logging information.")
    parser.add_argument(
        "endpoint",
        choices=["current", "historical"],
        nargs="?",
        help="Select which database to query: 'current' or 'historical'."
    )
    for field in VALID_SEARCH_FIELDS:
        parser.add_argument(
            f"--{field}",
            dest=field,
            type=str,
            help=f"Search query for '{field}'."
        )
    parser.add_argument(
        "--output",
        type=str,
        help="Specify a custom CSV output filename (overrides default naming)."
    )
    parser.add_argument(
        "--show",
        action="store_true",
        help="Display the CSV output on the terminal."
    )
    parser.add_argument(
        "--balance",
        action="store_true",
        help="Check API balance and print it to the terminal. If used, no reverse WHOIS query is performed."
    )

    # Parse arguments using the remaining_args from the preliminary parser.
    args = parser.parse_args(remaining_args)

    logging.debug("Parsed arguments: %s", args)

    # If --balance is specified, perform only the API balance check and exit.
    if args.balance:
        try:
            balance_response = check_api_balance(settings.API_KEY)
            current_balance = balance_response.get("current_balance")
            total_usage = balance_response.get("total_usage")
            if current_balance is not None and total_usage is not None:
                print("API Balance Information:")
                print(f"  Total API usage so far: {total_usage} credits.")
                print(f"  API credits remaining: {current_balance} credits.")
            else:
                print("Incomplete API balance information received.")
        except Exception:
            logging.exception("Failed to retrieve API balance information.")
            sys.exit(1)
        sys.exit(0)

    if not args.endpoint:
        print("Error: You must specify an endpoint ('current' or 'historical') unless using --balance.")
        sys.exit(1)

    # Build search parameters dictionary.
    search_params = {}
    for field in VALID_SEARCH_FIELDS:
        value = getattr(args, field)
        if value is not None:
            if "*" in value or "?" in value:
                logging.warning("Wildcard detected in '%s' with value '%s'. Using wildcards may cost additional API credits.", field, value)
            search_params[field] = value

    if not search_params:
        print("Error: No search fields provided. Please supply at least one search field argument (e.g., --domain_keyword yahoo).")
        sys.exit(1)

    logging.debug("Constructed search parameters: %s", search_params)

    try:
        response = query_api(args.endpoint, settings.API_KEY, search_params)
    except Exception:
        logging.exception("Reverse WHOIS query failed.")
        sys.exit(1)

    # Print a summary of the query response.
    success_status = response.get("success")
    count_info = response.get("count")
    stats_info = response.get("stats")
    print("Success:", success_status)
    total_matches = count_info.get("total", 0) if count_info else 0
    print(f"Count: Query returned {total_matches} matches")
    if stats_info and "api_credits_used" in stats_info:
        credits_used = stats_info["api_credits_used"]
    else:
        credits_used = "unknown"
    print(f"Query used {credits_used} API credits")

    results_data = response.get("results", [])
    if not results_data or (count_info and count_info.get("total", 0) == 0):
        print("No matches found for the query.")
    else:
        try:
            csv_filepath = write_csv(results_data, output_filename=args.output)
            print(f"Results saved to CSV file: {csv_filepath}")
            if args.show:
                print("\nCSV File Content:")
                with open(csv_filepath, "r", encoding="utf-8") as f:
                    print(f.read())
        except Exception:
            logging.exception("Failed to write CSV output.")
            sys.exit(1)

    logging.info("Script execution completed.")

# ------------------------------------------------------------------------------
if __name__ == "__main__":
    main()
