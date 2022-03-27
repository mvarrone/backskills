import os
import sqlite3

from dotenv import load_dotenv


def db_connection():
    load_dotenv()
    db_path = os.getenv('DB_PAYABLE_PATH')
    db_name = os.getenv('DB_PAYABLE_NAME')
    full_path = db_path + '\\' + db_name
    return sqlite3.connect(full_path)


def create_db_for_payables():
    conn = db_connection()

    c = conn.cursor()

    c.execute("""CREATE TABLE payableinfo (
        service_type TEXT,
        description TEXT,
        due_date TEXT,
        amount REAL,
        payment_status TEXT,
        barcode INTEGER PRIMARY KEY,
        payment_method TEXT,
        card_number INTEGER,
        amount_paid FLOAT,
        pay_date TEXT
        )""")

    conn.commit()
    conn.close()


def check_db_for_payables():
    load_dotenv()
    db_path = os.getenv('DB_PAYABLE_PATH')
    db_name = os.getenv('DB_PAYABLE_NAME')
    full_path = db_path + '\\' + db_name

    db_exists = os.path.isfile(full_path)
    if not(db_exists):
        create_db_for_payables()
        return "\nERROR: " + db_name + " not found.\nIt has been created in " + db_path + "\n"
    return "\nINFO: " + db_name + " found in " + db_path + "\nNo action has been performed\n"


if __name__ == "__main__":
    print(check_db_for_payables())
