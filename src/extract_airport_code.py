import pandas as pd
import requests
from bs4 import BeautifulSoup
import random
import string
import os
import re

def parse_airport_name(raw: str):
    """
    Given a raw airport name string like:
    'N'djili Airport (Kinshasa Int'l Airport) [1] (FAA: 0B8)'
    
    Returns:
      main_name: cleaned main airport name
      alt_name: alternate name (if any) or None
      extra_codes: any codes (FAA, TC, etc.) or 'None'
    """
    # remove reference tags like [1], [23]
    cleaned = re.sub(r'\[\d+\]', '', raw).strip()

    alt_name = None
    other_code = []

    # find all bracketed parts
    brackets = re.findall(r'\((.*?)\)', cleaned)

    # remove all brackets from the name
    main_name = re.sub(r'\(.*?\)', '', cleaned).strip().strip(',')

    for b in brackets:
        if re.search(r':', b):  # if it has colon, treat as code
            other_code.append(b.strip())
        else:
            alt_name = b.strip()

    other_codes = "; ".join(other_code) if other_code else ""
    alt_name = alt_name
    
    return main_name, alt_name, other_codes

def clean_text(text):
    # remove any text like [1], [23], etc.
    return re.sub(r'\[\d+\]', '', text).strip()

def fetch_airports_from_letter(letter: str) -> pd.DataFrame:
    """
    Fetch airports from a single Wikipedia page for a given letter.
    """
    url = f"https://en.wikipedia.org/wiki/List_of_airports_by_IATA_airport_code:_ {letter}"
    url = url.replace(" ", "")  # clean up
    print(f"Fetching from: {url}")
    resp = requests.get(url)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")

    # Find the first table
    table = soup.find("table", {"class": "wikitable"})
    if not table:
        raise ValueError(f"No table found on page for letter {letter}")

    rows = []
    for tr in table.find_all("tr")[1:]:  # skip header
        tds = tr.find_all(["td", "th"])
        if len(tds) >= 3:
            iata = clean_text(tds[0].get_text(strip=True))
            icao = clean_text(tds[1].get_text(strip=True))
            
            raw_name = tds[2].get_text(strip=True)
            airport_name, alt_name, other_codes = parse_airport_name(raw_name)
            
            rows.append({
                "iata_code": iata,
                "icao_code": icao,
                "airport_name": airport_name,
                "alt_name": alt_name,
                "other_codes": other_codes
            })

    return pd.DataFrame(rows)


def extract_airports(num_rows: int, output_csv: str = "../databank/airports_iata_icao.csv"):
    """
    Extract a specified number of airport records randomly over different letters.
    """
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)

    all_data = []
    letters = list(string.ascii_uppercase)
    random.shuffle(letters)

    while len(all_data) < num_rows and letters:
        letter = letters.pop()
        try:
            df = fetch_airports_from_letter(letter)
            all_data.append(df)
        except Exception as e:
            print(f"Skipping letter {letter} due to error: {e}")

    if not all_data:
        raise RuntimeError("No data could be fetched from any letter.")

    # concatenate and sample desired number of rows
    full_df = pd.concat(all_data, ignore_index=True)
    sample_df = full_df.sample(min(num_rows, len(full_df)), random_state=42).reset_index(drop=True)

    sample_df.to_csv(output_csv, index=False, encoding="utf-8")
    print(f"Saved {len(sample_df)} airport records to {output_csv}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Extract airport names, IATA and ICAO codes.")
    parser.add_argument("--n", type=int, help="Number of rows to extract")
    parser.add_argument("--output", type=str, default="../databank/airports_iata_icao.csv", help="Output CSV path")
    args = parser.parse_args()

    extract_airports(args.n, args.output)
