import csv
import random
import argparse
from typing import List, Dict
import os


def read_airports_from_csv(filepath: str) -> List[Dict[str, str]]:
    """Read airport data from CSV with columns: iata_code, icao_code, airport_name."""
    results = []
    with open(filepath, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            results.append({
                'iata_code': row.get('iata_code', '').strip(),
                'icao_code': row.get('icao_code', '').strip(),
                'airport_name': row.get('airport_name', '').strip(),
            })
    return results


def generate_questions(results: List[Dict[str, str]], num_questions: int, q_type: str) -> List[Dict[str, str]]:
    """
    Generate airport Q&A pairs of a specific type (iata or icao).
    Avoid duplicates and empty answers.
    """
    if not results:
        print("No results to generate questions from.")
        return []

    if q_type == "iata":
        template_str = "What is the IATA code for {airport_name}?"
        answer_key = "iata_code"
        validity_check = lambda r: bool(r['iata_code']) and bool(r['airport_name'])
    elif q_type == "icao":
        template_str = "What is the ICAO code for {airport_name}?"
        answer_key = "icao_code"
        validity_check = lambda r: bool(r['icao_code']) and bool(r['airport_name'])
    else:
        raise ValueError("q_type must be 'iata' or 'icao'.")

    questions_and_answers = []
    seen_questions = set()

    while len(questions_and_answers) < num_questions:
        r = random.choice(results)

        if not validity_check(r):
            continue

        question = template_str.format(airport_name=r['airport_name'])
        answer = r[answer_key]

        if question not in seen_questions:
            questions_and_answers.append({'question': question, 'answer': answer})
            seen_questions.add(question)

    return questions_and_answers


def split_train_test(data: List[Dict[str, str]], train_ratio: float):
    """Split data into train and test sets."""
    random.shuffle(data)
    split_idx = int(len(data) * train_ratio)
    return data[:split_idx], data[split_idx:]


def save_csv(data: List[Dict[str, str]], filepath: str):
    """Save list of dicts to CSV."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['question', 'answer'])
        writer.writeheader()
        writer.writerows(data)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate airport Q&A dataset.")
    parser.add_argument("--size", type=int, required=True, help="Total number of questions to generate.")
    parser.add_argument("--train", type=float, default=0.8, help="Train/test split ratio (default 0.8).")
    parser.add_argument("--type", type=str, required=True, choices=["iata", "icao"], help="Type of questions to generate.")
    parser.add_argument("--input", type=str, default="../databank/airports_iata_icao.csv", help="Input CSV file.")
    parser.add_argument("--output_dir", type=str, default="../databank", help="Output directory.")

    args = parser.parse_args()

    # Read data
    results = read_airports_from_csv(args.input)

    # Validate size and ratio
    if args.size < 1:
        raise ValueError("Size must be at least 1.")
    if not (0 < args.train < 1):
        raise ValueError("Train ratio must be between 0 and 1.")

    # Generate Q&A pairs
    qa_pairs = generate_questions(results, args.size, args.type)

    # Split
    train_set, test_set = split_train_test(qa_pairs, args.train)

    # Save with suffixes
    train_path = os.path.join(args.output_dir, f"SAmple_QA_airports_{args.type}_train.csv")
    test_path = os.path.join(args.output_dir, f"SAmple_QA_airports_{args.type}_test.csv")
    save_csv(train_set, train_path)
    save_csv(test_set, test_path)

    print(f"Saved {len(train_set)} train and {len(test_set)} test Q&A pairs.")
    print(f"Train file: {train_path}")
    print(f"Test file: {test_path}")
