file = open("input.txt","r")
file.read()


emi = years * 12
interest_amount = principle * years * interest / 100
total_amount = principle + interest_amount
emi_amount = total_amount / emi

loan_id.remaining_amount -= loan_id.emi_amount * emi


if lumsomes and lumsomes > 0:
    loan_id.remaining_amount -= lumsomes

new_emi = loan_id.remaining_amount / loan_id.emi_amount
loan_id.new_emi_count = round(new_emi)


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
