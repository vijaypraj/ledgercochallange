import sys
import datetime

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    ForeignKey,
    DATE,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


Base = declarative_base()

engine = create_engine("sqlite:///ledger.db")
Session = sessionmaker(bind=engine)
session = Session()


class Borrower(Base):
    __tablename__ = "borrower_master"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    bank = Column(String)


class Loan(Base):
    __tablename__ = "loan_master"

    id = Column(Integer, primary_key=True)
    borrower_id = Column(Integer, ForeignKey("borrower_master.id"))
    principle = Column(Float)
    years = Column(Float)
    interest = Column(Float)
    emi_count = Column(Float)
    new_emi_count = Column(Float)
    interest_amount = Column(Float)
    total_amount = Column(Float)
    emi_amount = Column(Float)
    remaining_amount = Column(Float)
    create_date = Column(DATE)


class Payment(Base):
    __tablename__ = "payment_master"

    id = Column(Integer, primary_key=True)
    borrower_id = Column(Integer, ForeignKey("borrower_master.id"))
    loan_id = Column(Integer, ForeignKey("loan_master.id"))
    lumsomes = Column(Integer)
    emi = Column(Integer)


Base.metadata.create_all(engine)


class Ledger(object):
    def __init__(self, *args):
        if len(sys.argv) > 1:
            if sys.argv[1] == "LOAN" and len(sys.argv) == 7:
                self.loan(
                    sys.argv[2] or "",
                    sys.argv[3] or "",
                    float(sys.argv[4]) or 0,
                    float(sys.argv[5]) or 0,
                    float(sys.argv[6]) or 0,
                )
            elif sys.argv[1] == "PAYMENT" and len(sys.argv) == 6:
                self.payment(
                    sys.argv[2] or "",
                    sys.argv[3] or "",
                    float(sys.argv[4]) or 0,
                    float(sys.argv[5]) or 0,
                )
            elif sys.argv[1] == "BALANCE" and len(sys.argv) == 5:
                self.balance(
                    sys.argv[2] or "", sys.argv[3] or "", float(
                        sys.argv[4]) or 0
                )
            else:
                print("Something went wrong! Check your imputs.")
        else:
            print("Something went wrong! Check your imputs.")

    def loan(self, bank, borrower, principle, years, interest):
        # Enter the loan details
        borrower_ids = (
            session.query(Borrower)
            .filter(Borrower.name == borrower, Borrower.bank == bank)
            .all()
        )
        if len(borrower_ids) == 0:
            borrower_id = Borrower(name=borrower, bank=bank)
            session.add(borrower_id)
            session.commit()
        else:
            borrower_id = borrower_ids[0]
        emi = years * 12
        interest_amount = principle * years * interest / 100
        total_amount = principle + interest_amount
        emi_amount = total_amount / emi
        loan_id = Loan(
            borrower_id=borrower_id.id,
            principle=principle,
            years=years,
            interest=interest,
            emi_count=round(emi),
            interest_amount=interest_amount,
            total_amount=round(total_amount),
            emi_amount=round(emi_amount),
            remaining_amount=round(total_amount),
            create_date=datetime.date.today(),
        )
        session.add(loan_id)
        session.commit()

    def payment(self, bank, borrower, lumsomes, emi):
        # Enter payment details
        borrower_ids = (
            session.query(Borrower)
            .filter(Borrower.name == borrower, Borrower.bank == bank)
            .all()
        )
        if len(borrower_ids) == 0:
            print("No borrower found!")
        else:
            borrower_id = borrower_ids[0]
        loan_ids = (
            session.query(Loan)
            .filter(Loan.borrower_id == borrower_id.id)
            .all()
        )
        if len(loan_ids) == 0:
            print("No loan found!")
        else:
            loan_id = loan_ids[0]

        payment_id = Payment(
            borrower_id=borrower_id.id,
            lumsomes=lumsomes,
            emi=emi,
            loan_id=loan_id.id,
        )
        session.add(payment_id)

        loan_id.remaining_amount -= loan_id.emi_amount * emi
        session.commit()

        if lumsomes and lumsomes > 0:
            loan_id.remaining_amount -= lumsomes
            session.commit()
            new_emi = loan_id.remaining_amount / loan_id.emi_amount
            loan_id.new_emi_count = round(new_emi)
            session.commit()

    def balance(self, bank, borrower, emi):
        # Return the balance
        borrower_ids = (
            session.query(Borrower)
            .filter(Borrower.name == borrower, Borrower.bank == bank)
            .all()
        )
        if len(borrower_ids) == 0:
            print("No borrower found!")
        else:
            borrower_id = borrower_ids[0]
        loan_ids = (
            session.query(Loan)
            .filter(Loan.borrower_id == borrower_id.id)
            .all()
        )

        if len(loan_ids) == 0:
            print("No loan found!")
        else:
            loan_id = loan_ids[0]
        payment_ids = (
            session.query(Payment)
            .filter(Payment.borrower_id == borrower_id.id, Payment.loan_id == loan_id.id)
            .all()
        )

        lumsum_paid = sum(payment.lumsomes for payment in payment_ids)
        emi_paid = loan_id.emi_amount * emi
        amount_paid = lumsum_paid + emi_paid

        emi_left = 0
        for payment in payment_ids:
            if payment.emi <= emi:
                emi_left = loan_id.new_emi_count - emi
                emi_left += loan_id.new_emi_count
            else:
                emi_left = loan_id.emi_count - emi
        print(bank, borrower, round(amount_paid),
              round(emi_left) if emi_left > 0 else 0)


if __name__ == "__main__":
    Ledger()
