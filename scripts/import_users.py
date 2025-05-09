import csv
from database.user_crud import create_user

CSV_PATH = r"C:\Users\Michail\PycharmProjects\IMEC_ver.3.1\data\users.csv"

def main():
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        count = 0
        for row in reader:
            email    = row["email"].strip()
            pwd_hash = row["password_hash"].strip()  # already a bcrypt hash
            role     = row.get("role", "user").strip() or "user"
            create_user(email=email, password_hash=pwd_hash, role=role)
            count += 1
    print(f"Imported {count} users")

if __name__ == "__main__":
    main()
