import os
import json
import re
import argparse
from bs4 import BeautifulSoup
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def extract_entities_from_directory(directory_path='./HTMLs'):
    extracted_data = []
    for file_name in os.listdir(directory_path):
        if file_name.endswith('.html'):
            file_path = os.path.join(directory_path, file_name)
            logging.debug(f"Processing file: {file_path}")  # Changed to DEBUG level
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    soup = BeautifulSoup(file, 'html.parser')
                    entities = soup.find_all('div', class_='linked-area')
                    for entity in entities:
                        name = None
                        name_tag = None
                        app_aware_links = entity.find_all('a', class_='app-aware-link')
                        for link in app_aware_links:
                            name_span = link.find('span', attrs={'aria-hidden': 'true'})
                            if name_span:
                                name_tag = link
                                name = name_span.get_text(strip=True)
                                break
                        linkedIn = None
                        if name_tag and name_tag.has_attr('href'):
                            linkedIn = name_tag['href'].split('?')[0]
                        company_tag = entity.find('p', class_='entity-result__summary')
                        company = company_tag.get_text(strip=True) if company_tag else None
                        if name or linkedIn or company:
                            extracted_data.append({
                                "Name": name,
                                "LinkedIn": linkedIn,
                                "Company": company
                            })
            except Exception as e:
                logging.error(f"Error processing file {file_path}: {e}")
    return extracted_data

def filter_data(data, filter_type):
    if filter_type == 'current':
        keyword = 'Current:'
    elif filter_type == 'past':
        keyword = 'Past:'
    else:
        return data
    filtered_data = [
        entry for entry in data 
        if entry.get("Company") and keyword in entry["Company"]
    ]
    return filtered_data

def extract_unique_company_names(data):
    unique_company_names = set()
    for entry in data:
        company_field = entry.get('Company', '')
        match = re.search(r'at\s+(.*?)(?:\s+-|$)', company_field)
        if match:
            company_name = match.group(1).strip()
            unique_company_names.add(company_name)
        else:
            unique_company_names.add('N/A')
    return sorted(unique_company_names)

def main():
    parser = argparse.ArgumentParser(description='Parse LinkedIn HTML files and extract company names.')
    parser.add_argument('-o', '--output', default='extracted_data.json', help='Output JSON file for extracted data.')
    parser.add_argument('-f', '--filter', choices=['current', 'past', 'all'], default='all', help='Filter by current or past companies.')
    parser.add_argument('-c', '--companies', help='Output file for unique company names.')
    args = parser.parse_args()

    directory_path = './HTMLs'
    logging.info('Starting to parse HTML files from ./HTMLs...')
    data = extract_entities_from_directory(directory_path)
    if not data:
        logging.error('No data extracted. Please check the HTML structure or script.')
        return
    else:
        logging.info(f'Data extracted from HTML files. Total records: {len(data)}')

    if args.filter != 'all':
        data = filter_data(data, args.filter)
        logging.info(f'Data filtered by {args.filter} companies. Records after filtering: {len(data)}')

    with open(args.output, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, indent=4, ensure_ascii=False)
    logging.info(f'Extracted data saved to {args.output}')

    if args.companies:
        unique_companies = extract_unique_company_names(data)
        with open(args.companies, 'w', encoding='utf-8') as output_file:
            for name in unique_companies:
                output_file.write(name + "\n")
        logging.info(f'Unique company names saved to {args.companies}')

if __name__ == '__main__':
    main()
