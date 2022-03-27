from datetime import date

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from db.db_actions import (create_payable_in_db, get_list_between_dates,
                           get_unpaid_payable_list,
                           get_unpaid_payable_list_by_type, make_transfer)
from schemas import Payable, Transaction
from utils import api_tags

load_dotenv()

description = """
API endpoints for backend
---

---
**Contact**

Author: Matías José Varrone

Email: mativarrone2@gmail.com

---
March, 2022
"""

tags_metadata = api_tags()

app = FastAPI(
    title="FastAPI Documentation",
    description=description,
    version="0.0.1",
    openapi_tags=tags_metadata,
    docs_url="/docs",
    redoc_url="/redoc",
)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@ app.post("/create-tax/", status_code=201, tags=["Payable"])
async def create_payable(payable: Payable):
    """
    Create payable

    *Parameters in body*

        service_type: (e.g. luz, agua, gas, etc)

        description: company name (e.g. Edenor S.A., Aguas Cordobesas S.A., MetroGAS S.A.)

        due_date: Expiration date (e.g. 2021-01-15). Format: YYYY-MM-DD

        amount: float

        payment_status: "pending"

        barcode: unique, 12 digits-length
    """
    return create_payable_in_db(payable.dict())


@ app.get("/unpaid-list/", status_code=200, tags=["Payable"])
async def get_unpaid_list():
    """
    Get an unpaid payable list

    *No parameters*

        Returns a list of every unpaid service (payment_status = pending)

    """
    return get_unpaid_payable_list()


@ app.get("/unpaid-list-by-service-type/{service_type}", status_code=200, tags=["Payable"])
async def get_unpaid_list_by_service_type(service_type: str):
    """
    Get an unpaid payable list by service_type

    *Parameter in path*

        service_type: luz, agua, gas, etc

    """
    result, length = get_unpaid_payable_list_by_type(service_type)
    if length == 0:
        raise HTTPException(
            status_code=404,
            detail="No elements to show")
    return result


@ app.put("/pay-tax/", status_code=201, tags=["Transaction"])
async def make_transaction(transaction: Transaction):
    """
    Make a pay

    *Parameters in body*

        pay_method: (e.g. "credit_card", "debit_card" or "cash")

        card_number: 16 digits-length

        amount: float

        barcode: unique, 12 digits-length

        paid_date: (e.g. 2021-01-15). Format: YYYY-MM-DD

    """
    return make_transfer(transaction.dict())


@ app.get("/get-transaction-list/", status_code=200, tags=["Transaction"])
async def get_transaction_list(start_date: date, final_date: date):
    """
    Get a transaction list between 2 dates given

        Returns a list of a date in particular, how many transactions were done that day and the amount accumulated

    *Parameters*

        start_date: (e.g. 2021-01-15). Format: YYYY-MM-DD
        final_date: (e.g. 2021-01-18). Format: YYYY-MM-DD

    """
    return get_list_between_dates(start_date, final_date)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=5001,
        reload=True,
        workers=4,
        # ssl_keyfile="./ssl_keys/cert.key",
        # ssl_certfile="./ssl_keys/cert.pem"
    )
