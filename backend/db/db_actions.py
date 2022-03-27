import json
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
            (:type, :descr, :due_date, :amount, :payment_status, :barcode, :paymentmethod, :cardnumber, :amountpaid, :paydate)",
            {
                'type': payable_fields["type"],
                'descr': payable_fields["descr"],
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

    return {"Status": "Payable registered successfully"}


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

    c.execute("""
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

    # print("\n", db_list)

    headers = ["barcode", "amount"]
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
        "SELECT type, due_date, amount, barcode FROM payableinfo where payment_status = ?", (status,)).fetchall()

    conn.close()

    # print("\n", db_list)

    headers = ["type", "due_date", "amount", "barcode"]
    resultado = []
    for _, element in enumerate(db_list):
        resultado.append(dict(zip(headers, list(element))))

    return resultado


def get_unpaid_payable_list_by_type(service_type):
    conn = db_connection()

    c = conn.cursor()

    status = "pending"

    db_list = c.execute(
        "SELECT due_date, amount, barcode FROM payableinfo where payment_status = ? AND type = ?", (status, service_type)).fetchall()

    conn.close()

    # print("\n", db_list)

    headers = ["due_date", "amount", "barcode"]
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

    # print("\n", db_list)

    headers = ["pay_date", "amount_paid", "counter"]
    resultado = []
    for _, element in enumerate(db_list):
        resultado.append(dict(zip(headers, list(element))))

    # print("\nresultado = ")
    # print(resultado)
    # print(type(resultado))
    # print(len(resultado))
    # print("\n")

    date_list = []
    for _, date in enumerate(resultado):
        # print(date)
        if date["pay_date"] not in date_list:
            date_list.append(date["pay_date"])

    # print("\ndate_list = ")
    # print(date_list)
    # print(len(date_list))
    # print(type(date_list))

    dictionary = {}
    lista_para_contador = []

    contador = 0
    acum = 0
    for idx, element in enumerate(date_list):
        for idx2, element2 in enumerate(resultado):
            # print(resultado[idx2]["amount_paid"])
            # print(date_list[idx])
            # print(resultado[idx2]["pay_date"])
            if date_list[idx] == resultado[idx2]["pay_date"]:
                contador = contador + 1
                acum = acum + resultado[idx2]["amount_paid"]
                # print(resultado[idx2]["amount_paid"])
        dictionary = {
            "date": date_list[idx],
            "number_of_transactions": contador,
            "amount_accumulated": acum
        }
        lista_para_contador.append(dictionary)
        # print(json.dumps(lista_para_contador, indent=2))
        contador = 0
        acum = 0

    return lista_para_contador
