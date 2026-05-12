import pandas as pd
import os
import random
import argparse

# Paths
GROUND_TRUTH_CSV = "../databank/roman_to_arabic.csv"
OUTPUT_DIR = "../databank"
TRAIN_SUFFIX = "_train.csv"
TEST_SUFFIX = "_test.csv"


def load_ground_truth(filepath):
    """Load roman→arabic pairs from CSV."""
    df = pd.read_csv(filepath)
    df = df.dropna(subset=["roman", "arabic"])
    df["arabic"] = df["arabic"].astype(str)
    return df


def generate_qa_pairs(df):
    """Generate unique Q–A pairs from DataFrame."""
    qa_list = []
    seen = set()
    for _, row in df.iterrows():
        roman = row["roman"].strip()
        arabic = row["arabic"].strip()
        q = f"What is the Arabic numeral for {roman}?"
        if q not in seen:
            seen.add(q)
            qa_list.append({"question": q, "answer": arabic})
    return qa_list


def split_train_test(qa_list, train_ratio=0.8):
    """Split Q–A list into train and test sets."""
    random.shuffle(qa_list)
    split_idx = int(len(qa_list) * train_ratio)
    train_set = qa_list[:split_idx]
    test_set = qa_list[split_idx:]
    return train_set, test_set


def save_csv(data, filepath):
    """Save Q–A pairs to CSV."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    df = pd.DataFrame(data)
    df.to_csv(filepath, index=False, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Generate Roman→Arabic numeral QA datasets.")
    parser.add_argument("--size", type=int, required=True,
                        help="Total number of Q–A pairs to generate (max from ground truth).")
    parser.add_argument("--train", type=float, default=0.8,
                        help="Ratio of training data (default: 0.8)")
    args = parser.parse_args()

    # Load ground-truth
    try:
        df = load_ground_truth(GROUND_TRUTH_CSV)
    except FileNotFoundError:
        print(f"Ground-truth file not found: {GROUND_TRUTH_CSV}")
        return

    if args.size < 1 or args.size > len(df):
        print(f"Error: size must be between 1 and {len(df)}")
        return

    if not (0 < args.train < 1):
        print("Error: train ratio must be between 0 and 1.")
        return

    # Sample & generate Q–A pairs
    sampled_df = df.sample(args.size, random_state=42).reset_index(drop=True)
    qa_pairs = generate_qa_pairs(sampled_df)

    # Split into train & test
    train_set, test_set = split_train_test(qa_pairs, args.train)

    # Save files
    train_path = os.path.join(OUTPUT_DIR, "QA_roman_to_arabic" + TRAIN_SUFFIX)
    test_path = os.path.join(OUTPUT_DIR, "QA_roman_to_arabic" + TEST_SUFFIX)

    save_csv(train_set, train_path)
    save_csv(test_set, test_path)

    # Summary
    print(f"Saved {len(train_set)} train pairs → {train_path}")
    print(f"Saved {len(test_set)} test pairs → {test_path}")


if __name__ == "__main__":
    main()
