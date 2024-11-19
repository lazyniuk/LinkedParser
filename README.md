
# LinkedIn HTML Parser
A Python-based utility for extracting, filtering, and processing data from LinkedIn HTML files. This tool helps extract user details, filter by current or past roles, and generate a list of unique company names.

## Features
- Parse LinkedIn HTML files for user details like names, LinkedIn profiles, and companies.
- Filter data by `Current:` or `Past:` roles.
- Generate unique company name lists for further processing.

## Usage Guide
### Extract All Data
    python3 parser.py

### Filter by Current or Past Roles
    python3 parser.py -f current -o current_data.json
    python3 parser.py -f past -o past_data.json

### Extract Unique Company Names
    python3 parser.py -i current_data.json -c companies.txt

### Directory Structure
    LinkedParser/
    ├── HTMLs/                # Directory containing LinkedIn HTML files
    ├── parser.py             # Main script for parsing and processing
    ├── extracted_data.json
    ├── current_data.json
    ├── past_data.json
    ├── companies.txt