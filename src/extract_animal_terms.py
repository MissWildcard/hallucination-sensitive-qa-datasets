import pandas as pd
import requests
import re

def clean_and_split_cell(text):
    """
    Clean and normalize a cell text:
      - remove refs like [12]
      - remove parenthetical info like (abc)
      - truncate if 'also see' appears
      - replace <br>, \n, or , with ;
      - if no separators but multiple single words, split
      - remove duplicates
    """
    if pd.isna(text):
        return ''
    text = str(text).strip()

    # Remove reference marks like [12]
    text = re.sub(r'\[[^\]]*\]', '', text)

    # Remove parenthetical info like (abc)
    text = re.sub(r'\([^)]*\)', '', text)

    # Truncate at 'also see' (case-insensitive)
    m = re.search(r'(?i)\balso\s+see\b', text)
    if m:
        text = text[:m.start()].strip()

    # Replace <br> and \n with ;
    text = re.sub(r'(<br\s*/?>|\n)+', ';', text)

    # Replace commas with ;
    text = text.replace(',', ';')

    # Collapse spaces
    text = re.sub(r'\s+', ' ', text).strip()

    # If already has separators
    if ';' in text:
        parts = [p.strip() for p in text.split(';') if p.strip()]
    else:
        # No separators; decide whether to split
        tokens = text.split()
        if len(tokens) > 1:
            parts = tokens
        else:
            parts = [text]

    # Remove duplicates
    seen = set()
    result = []
    for p in parts:
        if p not in seen:
            seen.add(p)
            result.append(p)

    return '; '.join(result)


def extract_animal_terms():
    url = "https://en.wikipedia.org/wiki/List_of_animal_names"
    resp = requests.get(url)
    resp.raise_for_status()

    tables = pd.read_html(resp.text)

    wanted_cols = ['animal', 'young', 'female', 'male', 'collective noun']
    target_table = None
    for t in tables:
        cols = [str(c).lower() for c in t.columns]
        if all(any(w in c for c in cols) for w in wanted_cols):
            target_table = t
            break

    if target_table is None:
        raise RuntimeError("Could not find table containing required columns.")

    if isinstance(target_table.columns, pd.MultiIndex):
        target_table.columns = [' '.join(map(str, c)).strip().lower() for c in target_table.columns]
    else:
        target_table.columns = [str(c).strip().lower() for c in target_table.columns]

    col_map = {}
    for w in wanted_cols:
        for c in target_table.columns:
            if w in c:
                col_map[w] = c
                break

    df_raw = target_table[[col_map[w] for w in wanted_cols]].copy()
    df_raw.columns = ['Animal', 'Young', 'Female', 'Male', 'Collective noun']

    # Clean cells
    for col in ['Animal', 'Young', 'Female', 'Male', 'Collective noun']:
        df_raw[col] = df_raw[col].apply(clean_and_split_cell)

    # Build clean records
    clean_rows = []
    current = None

    for _, row in df_raw.iterrows():
        animal = row['Animal']
        young  = row['Young']
        female = row['Female']
        male   = row['Male']
        coll   = row['Collective noun']

        # skip section headers
        if re.fullmatch(r'^[A-Z]$', animal):
            continue

        # skip rows where only animal has value
        if animal and all(x in ('', 'nan') for x in [young, female, male, coll]):
            continue

        if animal:  # new animal
            if current:
                clean_rows.append(current)

            current = {
                'Animal': animal,
                'Young': young,
                'Female': female,
                'Male': male,
                'Collective noun': coll
            }
        else:  # continuation row
            if coll and current:
                if current['Collective noun']:
                    current['Collective noun'] += ' / ' + coll
                else:
                    current['Collective noun'] = coll

    if current:
        clean_rows.append(current)

    df_clean = pd.DataFrame(clean_rows)

    # if female and male ended up identical because of bad source data, set male to empty
    df_clean.loc[df_clean['Female'] == df_clean['Male'], 'Male'] = ''

    return df_clean.reset_index(drop=True)


if __name__ == "__main__":
    df = extract_animal_terms()
    df.to_csv("../databank/animal_groups_and_names.csv", index=False)
    print(f"Saved {len(df)} rows to animal_groups_and_names.csv")
