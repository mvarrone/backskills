import os
import sqlite3

from dotenv import load_dotenv


def db_connection():
    load_dotenv()
    db_path = os.getenv('DB_PAYABLE_PATH')
    db_name = os.getenv('DB_PAYABLE_NAME')
    full_path = db_path + '\\' + db_name
    return sqlite3.connect(full_path)


def create_payable_in_db(payable_fields):
    conn = db_connection()

    c = conn.cursor()

    try:
        c.execute(
            "INSERT INTO payableinfo VALUES \
            (:service_type, :description, :due_date, :amount, :payment_status, :barcode, :paymentmethod, :cardnumber, :amountpaid, :paydate)",
            {
                'service_type': payable_fields["service_type"],
                'description': payable_fields["description"],
                'due_date': payable_fields["due_date"],
                'amount': payable_fields["amount"],
                'payment_status': payable_fields["payment_status"],
                'barcode': payable_fields["barcode"],
                'paymentmethod': "N/A",
                'cardnumber': 0,
                'amountpaid': 0.0,
                'paydate': "N/A"
            }
        )
    except sqlite3.IntegrityError as e:
        # e = UNIQUE constraint failed: payableinfo.barcode
        error_descr, details = e.args[0].split(": ")
        table_name, field = details.split(".")

        return {"Status": "ERROR: " + error_descr + ": " + field +
                " field must be an unique number in " + table_name + " table"}
    finally:
        conn.commit()
        conn.close

    return {
        "Status": "Payable registered successfully"
    }


def update_payable(transaction_fields, amount_in_db):
    conn = db_connection()

    # status = pending, paid, partially_paid

    if amount_in_db == transaction_fields["amount"]:
        payable_status = "paid"
    else:
        payable_status = "partially paid"

    if transaction_fields["pay_method"] == "cash":
        card_number = "N/A"
    else:
        card_number = transaction_fields["card_number"]

    c = conn.cursor()

    c.execute(
        """
    UPDATE payableinfo
    SET payment_status = :payment_status,
    amount = :amount,
    payment_method = :payment_method,
    card_number = :card_number,
    amount_paid = :amount_paid,
    pay_date = :pay_date
    WHERE barcode = ?""",
        (
            payable_status,
            amount_in_db - transaction_fields["amount"],
            transaction_fields["pay_method"],
            card_number,
            transaction_fields["amount"],
            transaction_fields["paid_date"],
            transaction_fields["barcode"]
        )
    )

    conn.commit()

    conn.close()

    return {
        "Status": "Payable has been " + payable_status,
        "Debt": amount_in_db - transaction_fields["amount"],
        "Barcode": transaction_fields["barcode"]
    }


def make_transfer(transaction_fields):
    conn = db_connection()

    c = conn.cursor()

    db_list = c.execute(
        "SELECT barcode, amount FROM payableinfo;").fetchall()

    conn.close()

    headers = [
        "barcode", "amount"
    ]
    resultado = []
    for _, barcode in enumerate(db_list):
        resultado.append(dict(zip(headers, list(barcode))))

    for _, elem in enumerate(resultado):
        if elem["barcode"] == transaction_fields["barcode"]:
            if int(elem["amount"]) == 0:
                return {
                    "Status": "There is no debt to pay",
                    "Debt": 0,
                    "Barcode": elem["barcode"]
                }
            if transaction_fields["amount"] > elem["amount"]:
                return {
                    "Status": "It is not possible to pay more than current debt",
                    "Debt": elem["amount"],
                    "Barcode": elem["barcode"]
                }
            return update_payable(transaction_fields, elem["amount"])


def get_unpaid_payable_list():
    conn = db_connection()

    c = conn.cursor()

    status = "pending"

    db_list = c.execute(
        "SELECT service_type, due_date, amount, barcode \
            FROM payableinfo where payment_status = ?", (status,)).fetchall()

    conn.close()

    headers = [
        "type", "due_date", "amount", "barcode"
    ]
    resultado = []
    for _, element in enumerate(db_list):
        resultado.append(dict(zip(headers, list(element))))

    return resultado


def get_unpaid_payable_list_by_type(service_type):
    conn = db_connection()

    c = conn.cursor()

    status = "pending"

    db_list = c.execute(
        "SELECT due_date, amount, barcode FROM payableinfo where payment_status = ? AND service_type = ?", (status, service_type)).fetchall()

    conn.close()

    headers = [
        "due_date", "amount", "barcode"
    ]
    resultado = []
    for _, element in enumerate(db_list):
        resultado.append(dict(zip(headers, list(element))))

    return resultado, len(resultado)


def get_list_between_dates(start_date, final_date):
    conn = db_connection()

    c = conn.cursor()

    status = "paid"

    db_list = c.execute(
        "SELECT pay_date, amount_paid, amount FROM payableinfo \
            where payment_status = ? AND \
                pay_date BETWEEN ? AND ?", (status, start_date, final_date, )).fetchall()

    conn.close()

    headers = [
        "pay_date", "amount_paid", "counter"
    ]
    resultado = []
    for _, element in enumerate(db_list):
        resultado.append(dict(zip(headers, list(element))))

    date_list = []
    for _, date in enumerate(resultado):
        if date["pay_date"] not in date_list:
            date_list.append(date["pay_date"])

    dictionary = {}
    counter = accumulator = 0
    result_list = []
    for i, _ in enumerate(date_list):
        for j, _ in enumerate(resultado):
            if date_list[i] == resultado[j]["pay_date"]:
                counter += 1
                accumulator += resultado[j]["amount_paid"]
        dictionary = {
            "date": date_list[i],
            "transaction_number_per_day": counter,
            "accumulated_amount_per_day": accumulator
        }
        result_list.append(dictionary)
        counter = accumulator = 0

    if len(result_list) == 0:
        return {
            "Status": "No transactions",
            "transaction_number_per_day": 0,
            "accumulated_amount_per_day": 0
        }
    return result_list[::-1]
