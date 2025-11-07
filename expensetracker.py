#!/usr/bin/env python3
import pandas as pd
import os
from datetime import datetime

FILE = "expenses.csv"
DATE_FMT = "%Y-%m-%d"
UNDO_STACK = []
if not os.path.exists(FILE):
    df = pd.DataFrame(columns=["date", "category", "amount", "note"])
    df.to_csv(FILE, index=False)


def load_data():
    return pd.read_csv(FILE)

def save_data(df):
    df.to_csv(FILE, index=False)

def today():
    return datetime.now().strftime(DATE_FMT)

def valid_date(s):
    try:
        datetime.strptime(s, DATE_FMT)
        return True
    except ValueError:
        return False


while True:
    print("\n=== SMART EXPENSE TRACKER ===")
    print("1) Add expense")
    print("2) Undo last add")
    print("3) List expenses (month or date range)")
    print("4) Search by note")
    print("5) Report (total, per category, max category)")
    print("0) Exit")
    choice = input("Select: ").strip()

    
    if choice == "1":
        df = load_data()
        date_str = input("Date (YYYY-MM-DD, blank=today): ").strip()
        if date_str == "":
            date_str = today()
        elif not valid_date(date_str):
            print("Invalid date.")
            continue

        category = input("Category: ").strip() or "Other"

        try:
            amount = float(input("Amount: ").strip())
            if amount <= 0:
                print("Amount must be positive.")
                continue
        except ValueError:
            print("Invalid number.")
            continue

        note = input("Note (optional): ").strip()

        new_row = {"date": date_str, "category": category, "amount": amount, "note": note}
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        save_data(df)
        UNDO_STACK.append(new_row)
        print("Added:", new_row)

    
    elif choice == "2":
        if not UNDO_STACK:
            print("Nothing to undo.")
            continue
        last = UNDO_STACK.pop()
        df = load_data()
        mask = (
            (df["date"] == last["date"]) &
            (df["category"] == last["category"]) &
            (df["amount"] == last["amount"]) &
            (df["note"] == last["note"])
        )
        if mask.any():
            df = df.loc[~mask]
            save_data(df)
            print("Undo successful:", last)
        else:
            print("Could not find record to undo.")

    # 3) List
    elif choice == "3":
        df = load_data()
        month = input("Month YYYY-MM (blank to skip): ").strip()
        if month:
            df = df[df["date"].str.startswith(month)]
        else:
            start = input("Start date YYYY-MM-DD (blank to skip): ").strip()
            end = input("End date YYYY-MM-DD (blank to skip): ").strip()
            if start:
                df = df[df["date"] >= start]
            if end:
                df = df[df["date"] <= end]

        if df.empty:
            print("No records found.")
        else:
            print("\n", df.to_string(index=False))

    
    elif choice == "4":
        df = load_data()
        keyword = input("Keyword in note: ").strip().lower()
        result = df[df["note"].fillna("").str.lower().str.contains(keyword)]
        if result.empty:
            print("No matches found.")
        else:
            print(result.to_string(index=False))

    
    elif choice == "5":
        df = load_data()
        month = input("Month YYYY-MM (blank to skip): ").strip()
        if month:
            df = df[df["date"].str.startswith(month)]
        else:
            start = input("Start date YYYY-MM-DD (blank to skip): ").strip()
            end = input("End date YYYY-MM-DD (blank to skip): ").strip()
            if start:
                df = df[df["date"] >= start]
            if end:
                df = df[df["date"] <= end]

        if df.empty:
            print("No data in this selection.")
            continue

        total = df["amount"].sum()
        per_category = df.groupby("category")["amount"].sum().sort_values(ascending=False)
        max_cat = per_category.idxmax()
        max_val = per_category.max()

        print("\n=== REPORT ===")
        print(f"Total spent: ₹{total:.2f}")
        print("\nBy category:")
        print(per_category.to_string())
        print(f"\nMax spend category: {max_cat} (₹{max_val:.2f})")


    elif choice == "0":
        print("Bye!")
        break

    else:
        print("Invalid choice.")
