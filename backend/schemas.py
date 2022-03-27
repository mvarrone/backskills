from datetime import date, datetime

from pydantic import BaseModel, validator


class Payable(BaseModel):
    service_type: str
    description: str
    due_date: date
    amount: float
    payment_status: str
    barcode: int

    @validator("due_date", pre=True)
    def parse_duedate_field(cls, value):
        return datetime.strptime(value, "%Y-%m-%d").date()

    @validator("barcode", pre=True)
    def parse_barcode_field(cls, value):
        length = len(str(value))
        if length == 12:
            return value
        raise ValueError(
            'barcode must be 12-digits length. Current: ' + str(length))


class Transaction(BaseModel):
    pay_method: str
    card_number: int = None
    amount: float
    barcode: int
    paid_date: date

    @validator("paid_date", pre=True)
    def parse_paid_date_field(cls, value):
        return datetime.strptime(value, "%Y-%m-%d").date()

    @validator("barcode", pre=True)
    def parse_barcode_field(cls, value):
        length = len(str(value))
        if length == 12:
            return value
        raise ValueError(
            'barcode must be 12-digits length. Current: ' + str(length))

    @validator("card_number", pre=True)
    def parse_card_number_field(cls, value):
        length = len(str(value))
        if length == 16:
            return value
        raise ValueError(
            'card number must be 16-digits length. Current: ' + str(length))
