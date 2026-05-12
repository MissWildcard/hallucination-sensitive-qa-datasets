import random
import csv
import os

CSV_FILE = "../databank/roman_to_arabic.csv"

def arabic_to_roman(num):
    if num <= 0 or num > 3999:
        return "Out of range"
    values = [1000, 900, 500, 400, 100, 90, 50, 40,
              10, 9, 5, 4, 1]
    symbols = ['M', 'CM', 'D', 'CD', 'C', 'XC', 'L', 'XL',
               'X', 'IX', 'V', 'IV', 'I']
    roman = ''
    for i in range(len(values)):
        count = num // values[i]
        roman += symbols[i] * count
        num -= values[i] * count
    return roman

def generate_unique_pairs(count):
    all_numbers = list(range(200, 4000))
    if count > len(all_numbers):
        raise ValueError(f"Only {len(all_numbers)} unique values available between 200 and 3999.")
    sampled = random.sample(all_numbers, count)
    return [(arabic_to_roman(n), n) for n in sampled]

def save_to_csv(pairs, filepath):
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["roman", "arabic"])
        writer.writerows(pairs)
    print(f"\n✅ Overwrote {filepath} with {len(pairs)} new pairs")

def main():
    try:
        n = int(input("How many Roman→Arabic pairs to generate (200–3999)? "))
        if n <= 0:
            raise ValueError
    except ValueError:
        print("❌ Please enter a valid positive number.")
        return

    try:
        new_pairs = generate_unique_pairs(n)
    except ValueError as e:
        print("⚠️", e)
        return

    print("\nSample of NEW Roman → Arabic Pairs:")
    print("=" * 45)
    for roman, arabic in new_pairs[:10]:  # preview
        print(f"{roman:12s} → {arabic}")

    save_to_csv(new_pairs, CSV_FILE)

if __name__ == "__main__":
    main()
