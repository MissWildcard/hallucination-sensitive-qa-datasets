import pandas as pd
import random
import os
import argparse

def is_valid(value: str) -> bool:
    return value.strip() not in ["", "(none)", "—", ""]

def parse_answers(value: str) -> list:
    return [v.strip() for v in value.split(";") if is_valid(v)]

def main():
    parser = argparse.ArgumentParser(description="Generate animal Q&A dataset.")
    parser.add_argument("--size", type=int, required=True, help="Total number of questions to generate.")
    parser.add_argument("--train", type=float, default=0.8, help="Train/test split ratio (default 0.8).")
    parser.add_argument("--type", type=str, required=True,
                        choices=["male", "female", "young", "collective"],
                        help="Type of questions to generate.")
    parser.add_argument("--input", type=str, default="../databank/animal_groups_and_names.csv",
                        help="Input CSV file.")
    parser.add_argument("--output_dir", type=str, default="../databank",
                        help="Output directory.")
    args = parser.parse_args()

    # Load data
    df = pd.read_csv(args.input).fillna("")

    # Map argument to column name & template
    col_map = {
        "male": "Male",
        "female": "Female",
        "young": "Young",
        "collective": "Collective noun"
    }
    template_map = {
        "male": "What is the male {animal} called?",
        "female": "What is the female {animal} called?",
        "young": "What is the young one of a/an {animal} called?",
        "collective": "What is a group of {animal} called?"
    }

    target_col = col_map[args.type]
    template = template_map[args.type]

    # Generate questions
    seen_questions = set()
    qa_pairs = []

    for _ in range(args.size * 3):  # oversample to avoid duplicates
        row = df.sample(1).iloc[0]
        answers = parse_answers(row[target_col])
        if not answers:
            continue

        q_text = template.format(animal=row["Animal"])
        if q_text in seen_questions:
            continue

        qa_pairs.append({"question": q_text, "answers": "; ".join(answers)})
        seen_questions.add(q_text)

        if len(qa_pairs) >= args.size:
            break

    # Shuffle before splitting
    random.shuffle(qa_pairs)

    # Split into train/test
    split_idx = int(len(qa_pairs) * args.train)
    train_data = qa_pairs[:split_idx]
    test_data = qa_pairs[split_idx:]

    # Prepare filenames
    train_csv = os.path.join(args.output_dir, f"QA_animals_{args.type}_train.csv")
    test_csv = os.path.join(args.output_dir, f"QA_animals_{args.type}_test.csv")

    # Save
    os.makedirs(args.output_dir, exist_ok=True)
    pd.DataFrame(train_data).to_csv(train_csv, index=False, encoding="utf-8")
    pd.DataFrame(test_data).to_csv(test_csv, index=False, encoding="utf-8")

    print(f"Saved {len(train_data)} training questions → {train_csv}")
    print(f"Saved {len(test_data)} testing questions → {test_csv}")

if __name__ == "__main__":
    main()
