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
      logging.debug(f"Processing file: {file_path}")
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
  keywords = {'current': 'Current:', 'past': 'Past:'}
  keyword = keywords.get(filter_type)
  if not keyword:
    return data
  return [entry for entry in data if entry.get("Company") and keyword in entry["Company"]]

def extract_unique_company_names(data):
  unique_companies = set()
  for entry in data:
    company_field = str(entry.get('Company', '') or '')
    match = re.search(r'at\s+(.*?)(?:\s+-|$)', company_field)
    if match:
      unique_companies.add(match.group(1).strip())
    else:
      unique_companies.add('N/A')
  return sorted(unique_companies)

def main():
  parser = argparse.ArgumentParser(description='Parse LinkedIn HTML files and extract company names.')
  parser.add_argument('-i', '--input', default='extracted_data.json', help='Input JSON file for filtering or company extraction.')
  parser.add_argument('-o', '--output', default='extracted_data.json', help='Output JSON file for extracted or filtered data.')
  parser.add_argument('-f', '--filter', choices=['current', 'past', 'all'], default='all', help='Filter by current or past companies.')
  parser.add_argument('-c', '--companies', help='Output file for unique company names.')
  args = parser.parse_args()

  if args.companies:
    with open(args.input, 'r', encoding='utf-8') as json_file:
      data = json.load(json_file)
    unique_companies = extract_unique_company_names(data)
    with open(args.companies, 'w', encoding='utf-8') as output_file:
      output_file.write('\n'.join(unique_companies))
    logging.info(f'Unique company names saved to {args.companies}')
  else:
    if args.filter == 'all':
      directory_path = './HTMLs'
      logging.info('Starting to parse HTML files from ./HTMLs...')
      data = extract_entities_from_directory(directory_path)
      with open(args.output, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, indent=4, ensure_ascii=False)
      logging.info(f'Extracted data saved to {args.output}')
    else:
      with open(args.input, 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)
      data = filter_data(data, args.filter)
      with open(args.output, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, indent=4, ensure_ascii=False)
      logging.info(f'Filtered data saved to {args.output}')

if __name__ == '__main__':
  main()
