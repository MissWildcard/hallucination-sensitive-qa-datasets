import re
import csv
import os
from typing import List, Dict
import wikipedia


def fetch_wikipedia_page(page_title: str) -> str:
    """
    Fetch the text content of a Wikipedia page.
    """
    try:
        page = wikipedia.page(page_title)
        return page.content
    except Exception as e:
        print(f"Error fetching Wikipedia page: {e}")
        return ""


def extract_units_and_entities(text: str) -> List[Dict[str, str]]:
    """
    Extract units and their corresponding physical entities from text.
    Splits alternative units (with 'or' or 'also') into separate rows.
    """

    # regex to catch 3-letter headings.
    #the headings are wrpped with ===. For eg: === MTS ===
    heading_re = re.compile(r'^=+\s*([A-Z]{3})\s*=+$')

    patterns = [
        # The unit (symbol) or unit2 (symbol2) …
        r'The\s+([^(]+?)\s*\(([^)]+?)\)\s+(?:or|also)\s+([^(]+?)\s*\(([^)]+?)\)\s+is\s+a\s+(?:non-coherent\s+)?unit\s+of\s+(.+?)(?=,|\s+(?:equal\s+to|corresponding\s+to|used\s+in|defined\s+as)|\.|;|$)',
        # The unit (symbol) …
        r'The\s+([^(]+?)\s*\(([^)]+?)\)\s+is\s+a\s+(?:non-coherent\s+)?unit\s+of\s+(.+?)(?=,|\s+(?:equal\s+to|corresponding\s+to|used\s+in|defined\s+as)|\.|;|$)',
        # The unit …
        r'The\s+([A-Za-z\-\s]+?)\s+is\s+a\s+(?:non-coherent\s+)?unit\s+of\s+(.+?)(?=,|\s+(?:equal\s+to|corresponding\s+to|used\s+in|defined\s+as)|\.|;|$)'
    ]

    results = []
    lines = text.split('\n')
    current_heading = None

    for line in lines:
        line = line.strip()
        if not line or (line.startswith('*') and not line.startswith('* The')):
            continue
        print(line)
        # Check for heading
        if heading_re.match(line):
            print('found heading @ {line}')
            current_heading = line
            continue

        # Remove markdown formatting
        line = re.sub(r'^\*\s*', '', line)
        line = re.sub(r'\[edit\]', '', line)
        line = re.sub(r'\*([^*]+)\*', r'\1', line)

        for pattern in patterns:
            matches = re.findall(pattern, line, re.IGNORECASE)

            for match in matches:
                if len(match) == 5:  # two units
                    unit1, sym1, unit2, sym2, entity = map(str.strip, match)

                    for unit_name, symbol in [(unit1, sym1), (unit2, sym2)]:
                        unit_name = re.sub(r'\s+', ' ', unit_name)
                        entity_clean = re.sub(r'\s+', ' ', entity)

                        if any(word in entity_clean.lower() for word in ['equal', 'also', 'symbol']):
                            continue

                        result_dict = {
                            'unit': unit_name,
                            'symbol': symbol,
                            'entity': entity_clean,
                            'system_of_units': current_heading or ""
                        }

                        if not any(r['unit'].lower() == unit_name.lower() and r['entity'].lower() == entity_clean.lower()
                                   for r in results):
                            results.append(result_dict)

                    break  # stop after first match on this line

                elif len(match) == 3:  # single unit
                    unit_name, symbol, entity = map(str.strip, match)

                    unit_name = re.sub(r'\s+', ' ', unit_name)
                    entity_clean = re.sub(r'\s+', ' ', entity)

                    if any(word in entity_clean.lower() for word in ['equal', 'also', 'symbol']):
                        continue

                    result_dict = {
                        'unit': unit_name,
                        'symbol': symbol,
                        'entity': entity_clean,
                        'system_of_units': current_heading or ""
                    }

                    if not any(r['unit'].lower() == unit_name.lower() and r['entity'].lower() == entity_clean.lower()
                               for r in results):
                        results.append(result_dict)

                    break  # stop after first match on this line

                elif len(match) == 2:  # no symbol
                    unit_name, entity = map(str.strip, match)

                    unit_name = re.sub(r'\s+', ' ', unit_name)
                    entity_clean = re.sub(r'\s+', ' ', entity)

                    if any(word in entity_clean.lower() for word in ['equal', 'also', 'symbol']):
                        continue

                    result_dict = {
                        'unit': unit_name,
                        'symbol': "",
                        'entity': entity_clean,
                        'system_of_units': current_heading or ""
                    }

                    if not any(r['unit'].lower() == unit_name.lower() and r['entity'].lower() == entity_clean.lower()
                               for r in results):
                        results.append(result_dict)

                    break  # stop after first match on this line

    return results


def normalize_results(results: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    Post-process results: split units/symbols with 'or', clean 'symbol' keyword, deduplicate.
    Also cleans the system_of_units field.
    """
    normalized = []
    seen = set()

    def clean_system(system_str: str) -> str:
        match = re.match(r'^=+\s*([A-Z]{3})\s*=+$', system_str.strip())
        if match:
            return match.group(1)
        return system_str.strip()

    for r in results:
        units = [u.strip() for u in re.split(r'\s+or\s+', r['unit']) if u.strip()]
        symbols = [s.strip() for s in re.split(r'\s+or\s+', r['symbol']) if s.strip()]
        entity = r['entity'].strip()
        system_of_units = clean_system(r.get('system_of_units', ''))

        symbols = [re.sub(r'\bsymbol\b', '', s, flags=re.IGNORECASE).strip() for s in symbols]

        if not symbols:
            symbols = [""]

        for u in units:
            for s in symbols:
                key = (u.lower(), s.lower(), entity.lower(), system_of_units.lower())
                if key not in seen:
                    seen.add(key)
                    normalized.append({
                        'unit': u,
                        'symbol': s,
                        'entity': entity,
                        'system_of_units': system_of_units
                    })

    return normalized



def print_results(results: List[Dict[str, str]]) -> None:
    """
    Print the extracted results in a formatted way.
    """
    print("\nExtracted Units and Entities:")
    print("-" * 50)

    for i, result in enumerate(results, 1):
        print(f"{i}. Unit: {result['unit']}")
        if result['symbol']:
            print(f"   Symbol: {result['symbol']}")
        print(f"   Entity: {result['entity']}")
        if 'system_of_units' in result and result['system_of_units']:
            print(f"   System of Units Heading: {result['system_of_units']}")
        print()


def save_results_to_csv(results: List[Dict[str, str]], filepath: str) -> None:
    """
    Save extracted results to a CSV file.
    """

    # Create parent directory if missing
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    # Add system_of_units to fieldnames if present in results
    fieldnames = ['unit', 'symbol', 'entity']
    if any('system_of_units' in r for r in results):
        fieldnames.append('system_of_units')

    with open(filepath, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Results saved to {filepath}")



def main():
    # Specify the Wikipedia page title
    page_title = "List of metric units"
    print(f"Fetching Wikipedia page: {page_title}")
    text = fetch_wikipedia_page(page_title)

    if not text:
        print("Failed to load Wikipedia page.")
        return

    extracted_data = extract_units_and_entities(text)

    if extracted_data:
        normalized_data = normalize_results(extracted_data)
        print_results(normalized_data)
        output_path = os.path.join("..", "databank", "units_and_quantities.csv")
        save_results_to_csv(normalized_data, output_path)
    else:
        print("No matching units/entities found.")

if __name__ == "__main__":
    main()
