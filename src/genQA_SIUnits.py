import csv
import random
import argparse
import os
from typing import List, Dict

def generate_questions(
    results: List[Dict[str, str]],
    num_questions: int,
    q_type: str
) -> List[Dict[str, str]]:
    """
    Generate Q&A pairs for a given question type, capped at maximum possible unique questions.
    """
    templates_map = {
        "unit": [
            ("In the {system} system of units, what is the unit of {entity}?",
             lambda r: r['unit'],
             lambda r: True)
        ],
        "quantity": [
            ("In the {system} system of units, what quantity does the unit {unit} represent?",
             lambda r: r['entity'],
             lambda r: True)
        ],
        "symbol": [
            ("In the {system} system of units, what is the symbol of the unit {unit}?",
             lambda r: r['symbol'],
             lambda r: bool(r['symbol'].strip()))
        ]
    }

    if q_type not in templates_map:
        raise ValueError(f"Invalid question type: {q_type}")

    templates = templates_map[q_type]
    seen_questions = set()
    questions_and_answers = []

    # First, build ALL possible valid QAs for this type
    for r in results:
        for template_str, answer_fn, is_valid in templates:
            if not is_valid(r):
                continue
            question = template_str.format(
                system=r.get('system_of_units', '').strip() or "UNKNOWN",
                entity=r.get('entity', '').strip(),
                unit=r.get('unit', '').strip()
            )
            answer = answer_fn(r).strip()
            if question and answer and question not in seen_questions:
                seen_questions.add(question)
                questions_and_answers.append({
                    'question': question,
                    'answer': answer
                })

    # Cap size at available max
    if num_questions > len(questions_and_answers):
        print(f"Requested {num_questions} Qs but only {len(questions_and_answers)} possible. Using max available.")
        num_questions = len(questions_and_answers)

    random.shuffle(questions_and_answers)
    return questions_and_answers[:num_questions]


def read_results_from_csv(filepath: str) -> List[Dict[str, str]]:
    """
    Read the units data from a CSV file.
    """
    results = []
    with open(filepath, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            results.append({
                'unit': row.get('unit', '').strip(),
                'symbol': row.get('symbol', '').strip(),
                'entity': row.get('entity', '').strip(),
                'system_of_units': row.get('system_of_units', '').strip()
            })
    return results


def save_split(train_data, test_data, output_dir, q_type):
    """
    Save train/test CSVs with _train/_test and _qtype suffix.
    """
    os.makedirs(output_dir, exist_ok=True)
    train_path = os.path.join(output_dir, f"QA_uqs_{q_type}_train.csv")
    test_path = os.path.join(output_dir, f"QA_uqs_{q_type}_test.csv")

    with open(train_path, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['question', 'answer'])
        writer.writeheader()
        writer.writerows(train_data)

    with open(test_path, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['question', 'answer'])
        writer.writeheader()
        writer.writerows(test_data)

    print(f"Saved {len(train_data)} train questions → {train_path}")
    print(f"Saved {len(test_data)} test questions → {test_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Q-A dataset for units and quantities.")
    parser.add_argument("--input", type=str, default="../databank/units_and_quantities.csv", help="Input CSV file")
    parser.add_argument("--output_dir", type=str, default="../databank", help="Output directory")
    parser.add_argument("--size", type=int, required=True, help="Number of questions to generate")
    parser.add_argument("--train", type=float, default=0.8, help="Train/test split ratio")
    parser.add_argument("--type", type=str, required=True, choices=["unit", "quantity", "symbol"], help="Type of question to generate")
    args = parser.parse_args()

    results = read_results_from_csv(args.input)
    qa_pairs = generate_questions(results, args.size, args.type)

    split_idx = int(len(qa_pairs) * args.train)
    train_data = qa_pairs[:split_idx]
    test_data = qa_pairs[split_idx:]

    save_split(train_data, test_data, args.output_dir, args.type)
