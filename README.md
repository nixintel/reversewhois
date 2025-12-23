# Reverse WHOIS

This Python script is intended to work with the Big Domain Data API. You will need to create an account and purchase an API key to perform lookups. Currently $5 = 5000 credits.

It allows users to query current and historical WHOIS records using a range of parameters such as creation dates, registrant_email, domain keyword, and many others. The script also supports bulk WHOIS queries to retrieve information for multiple domains simultaneously. The bulk WHOIS lookup only works with the current WHOIS database, not the historical one.

The API also allows wildcard searches. Wildcard searches may use more API credits than standard queries.

I strongly recommend that you read the API docs first. 

https://www.bigdomaindata.com/guide.php#reverse-whois

## Setup

To download and install:

`git clone https://github.com/nixintel/reversewhois`

`cd reversewhois`

Create a virtual environment and activate it.

`python3 -m venv .`

`source bin/activate`

`pip install -r requirements.txt`

Add your API key to the `settings.py` file. 

Check it is working.

`python3 main.py --help`


## Basic Usage

Big Domain Data has two WHOIS databases for reverse lookups: `current` and `historical`. You need to specify one of these when making a reverse WHOIS query.

The differences are explained here:

https://www.bigdomaindata.com/historical-whois-database/

https://www.bigdomaindata.com/current-whois-database/

For bulk WHOIS queries (retrieving information about multiple specific domains), use the `bulk` endpoint instead.

https://www.bigdomaindata.com/bulk-whois-api/ 

Some other useful options:

```
--domains DOMAINS         Comma-separated list of domains for bulk WHOIS query (e.g., yahoo.com,google.com).
--domains-file FILE       Path to file containing domains (one per line) for bulk WHOIS query.
--output OUTPUT           Specify a custom CSV output filename (overrides default naming).
--show                    Display the CSV output on the terminal.
--balance                 Check API balance and print it to the terminal. If used, no WHOIS query is performed.
--debug                   Turn on debugging mode
```

All results are saved in CSV format in the `results` folder use the date and time for the filename. This can be manually overridden using the `--output` option.

## Sample Input Files for Bulk WHOIS Queries

Two sample input files are provided in the repository for your convenience:

- **`sample_text_input_file.txt`** - A plain text file with example domains (one per line)
- **`sample_csv_input_file.csv`** - A CSV file with example domains (one per line)

**How to use them:**

1. Copy one of the sample files to create your own
2. Edit the file and replace the example domains with your own domains (one domain per line)
3. Save the file
4. Run the bulk query: `python3 main.py bulk --domains-file your_file.txt`

Both file formats work identically - choose whichever format you're most comfortable with. The script simply reads domains line by line from the file.

## Example queries

### Reverse WHOIS Examples

All domains registered with Namecheap (IANA number 1068) on 1st August 2024:

`python3 main.py current --registrar_iana 1068 --create_date 2024-08-01`

All domains registered during the final week of 2024 that used the nameserver `suzanne.ns.cloudflare.com`

`python3 main.py current --name_server suzanne.ns.cloudflare.com --create_date_from 2024-12-24 --create_date_to 2024-12-31`

Find historical domains that were registered with an FBI email address:

`python3 main.py historical --registrant_email_wildcard *@fbi.gov`

Find any domain registered in January 2025 that contained the keyword "Facebook".

`python3 main.py current --domain_keyword_wildcard facebook* --create_date_from 2025-01-01 --create_date_to 2025-01-31`

### Bulk WHOIS Examples

Query multiple domains using comma-separated list:

`python3 main.py bulk --domains yahoo.com,google.com,facebook.com,twitter.com,amazon.com`

Query domains from a text file (one domain per line):

`python3 main.py bulk --domains-file domains.txt`

Query domains using the provided sample files:

`python3 main.py bulk --domains-file sample_text_input_file.txt`

`python3 main.py bulk --domains-file sample_csv_input_file.csv`

Bulk query with custom output filename:

`python3 main.py bulk --domains yahoo.com,google.com,amazon.com --output my_bulk_results`

Bulk query and display results in terminal:

`python3 main.py bulk --domains yahoo.com,google.com --show`