# Reverse WHOIS

This Python script is intended to work with the Big Domain Data API. You will need to create an account and purchase an API key to perform lookups. Currently $5 = 5000 credits.

It allows users to query current and historical WHOIS records using a range of parameters such as creation dates, registrant_email, domain keyword, and many others.

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

Big Domain Data has two WHOIS databases, `current` and `historical`. You need to specify one of these when making a query.

The differences are explained here:

https://www.bigdomaindata.com/historical-whois-database/
https://www.bigdomaindata.com/current-whois-database/

Some other useful options:

```
--output OUTPUT       Specify a custom CSV output filename (overrides default naming).
  --show                Display the CSV output on the terminal.
  --balance             Check API balance and print it to the terminal. If used, no reverse WHOIS query is performed.
  --debug               Turn on debugging mode
```

All results are saved in CSV format in the `results` folder use the date and time for the filename. This can be manually overridden using the `--output` option.

## Example queries

All domains registered with Namecheap (IANA number 1068) on 1st August 2024:

`python3 main.py current --registrar_iana 1068 --create_date 2024-08-01`

All domains registered during the final week of 2025 that used the nameserver `suzanne.ns.cloudflare.com`

`python3 main.py current --name_server suzanne.ns.cloudflare.com --create_date_from 2024-12-24 --create_date_to 2024-12-31`

Find historical domains that were registered with an FBI email address:

`python3 main.py historical --registrant_email_wildcard *@fbi.gov`

Find any domain registered in January 2025 that contained the keyword "Facebook".

`python3 main.py current --domain_keyword_wildcard facebook* --create_date_from 2025-01-01 --create_date_to 2025-01-31`