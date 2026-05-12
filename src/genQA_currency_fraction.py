import pandas as pd
import random
import os
import argparse

def is_valid(value: str) -> bool:
    """Check if a value is meaningful: not empty and not '(none)'."""
    return value.strip() != "" and value.strip().lower() != "(none)"

# ---------------------- ARGUMENTS ----------------------
parser = argparse.ArgumentParser(description="Generate currency Q-A dataset.")
parser.add_argument("--size", type=int, default=100, help="Number of questions to generate")
parser.add_argument("--train_ratio", type=float, default=0.8, help="Ratio of data to use for training")
parser.add_argument("--qtype", type=str, choices=["iso_code", "symbol_or_abbreviation", "fractional_unit", "all"],
                    default="all", help="Type of question to generate")
args = parser.parse_args()

input_csv = "../databank/currencies_and_fractions.csv"
output_dir = "../databank/"

# ---------------------- LOAD DATA ----------------------
df = pd.read_csv(input_csv)
df = df.fillna("")

# ---------------------- TEMPLATES ----------------------
all_templates = {
    "fractional_unit": "What is the fractional unit of the currency {currency} from {country}?",
    "iso_code": "What is the ISO code of the currency {currency} from {country}?",
    "symbol_or_abbreviation": "What is the currency symbol of the currency {currency} from {country}?"
}

# Select templates based on qtype argument
if args.qtype == "all":
    selected_templates = all_templates
else:
    selected_templates = {args.qtype: all_templates[args.qtype]}

# ---------------------- GENERATE QUESTIONS ----------------------
questions = []

while len(questions) < args.size:
    row = df.sample(1).iloc[0]
    valid_templates = []

    for qtype, template in selected_templates.items():
        if is_valid(row[qtype]):
            valid_templates.append((template, qtype))

    if not valid_templates:
        if args.qtype == "all":
            valid_templates = [(all_templates["symbol_or_abbreviation"], "symbol_or_abbreviation")]
        else:
            continue

    template, col = valid_templates[0]
    q = template.format(currency=row["currency"], country=row["country"])
    a = row[col]
    questions.append({"question": q, "answer": a})

# ---------------------- SHUFFLE & SPLIT TRAIN / TEST ----------------------
random.shuffle(questions)
n_train = int(len(questions) * args.train_ratio)
train_questions = questions[:n_train]
test_questions = questions[n_train:]

# ---------------------- SAVE CSVS ----------------------
os.makedirs(output_dir, exist_ok=True)

def save_questions(q_list, split):
    qtype_suffix = args.qtype if args.qtype != "all" else "all"
    output_csv = os.path.join(output_dir, f"QA_currencies_{qtype_suffix}_{split}.csv")
    pd.DataFrame(q_list).to_csv(output_csv, index=False, encoding="utf-8")
    print(f"Saved {len(q_list)} questions → {output_csv}")

save_questions(train_questions, "train")
save_questions(test_questions, "test")
