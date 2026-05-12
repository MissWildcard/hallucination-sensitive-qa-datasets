import pandas as pd
import random
import os
import argparse

def main():
    parser = argparse.ArgumentParser(description="Generate Q-A pairs for books and authors.")
    parser.add_argument("--input", type=str, default="../databank/books_and_authors.csv", help="Input CSV path")
    parser.add_argument("--output_dir", type=str, default="../databank", help="Directory to save outputs")
    parser.add_argument("--size", type=int, default=100, help="Total number of Q-A pairs to generate")
    parser.add_argument("--train", type=float, default=0.8, help="Ratio of data for training set")
    args = parser.parse_args()

    # Load and clean data
    df = pd.read_csv(args.input)
    df = df.dropna(subset=["title", "author"])

    df["title"] = df["title"].astype(str).str.strip().str.replace(r'^"+|"+$', '', regex=True)
    df["title"] = df["title"].str.replace(r'""+', '"', regex=True)
    df["author"] = df["author"].astype(str).str.strip()

    # Single question template
    template = "Who is the author of the book \"{title}\"?"

    # Shuffle and sample
    df_sampled = df.sample(frac=1, random_state=42).head(args.size)

    questions = []
    seen_questions = set()

    for _, row in df_sampled.iterrows():
        title = row["title"]
        author = row["author"]

        q_text = template.format(title=title)

        if q_text not in seen_questions:
            seen_questions.add(q_text)
            questions.append({
                "question": q_text,
                "answers": author
            })

        if len(questions) >= args.size:
            break

    # Split train/test
    split_idx = int(len(questions) * args.train)
    train_df = pd.DataFrame(questions[:split_idx])
    test_df = pd.DataFrame(questions[split_idx:])

    # Ensure output dir exists
    os.makedirs(args.output_dir, exist_ok=True)

    # Save with suffix
    train_path = os.path.join(args.output_dir, f"QA_books_authors_train.csv")
    test_path = os.path.join(args.output_dir, f"QA_books_authors_test.csv")

    train_df.to_csv(train_path, index=False, encoding="utf-8")
    test_df.to_csv(test_path, index=False, encoding="utf-8")

    print(f"Saved {len(train_df)} questions to {train_path}")
    print(f"Saved {len(test_df)} questions to {test_path}")

if __name__ == "__main__":
    main()
