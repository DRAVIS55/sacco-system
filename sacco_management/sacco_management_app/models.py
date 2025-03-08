from django.db import models
from django.contrib.auth.models import User
from datetime import date
from django.utils.timezone import now
# Create your models here.
from django.contrib.auth.hashers import make_password
from django.dispatch import receiver
from django.db.models.signals import post_save
from datetime import timedelta


from django.db import models

class Loan(models.Model):
    loan_id = models.AutoField(primary_key=True)
    member = models.ForeignKey('Member', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    start_date = models.DateField()
    due_date = models.DateField()
    status = models.CharField(
        max_length=15, 
        choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Paid', 'Paid')]
    )

    def __str__(self):
        return f"Loan {self.loan_id} - {self.member.first_name}"


# ✅ Define LoanRepayment **after** Loan to avoid NameError
class LoanRepayment(models.Model):
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Repayment for Loan {self.loan.loan_id} - Ksh. {self.amount_paid}"

# ------------------------------
# MEMBER SAVINGS MODEL
# ------------------------------
class Savings(models.Model):
    member = models.ForeignKey("Member", on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    deposit_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Savings {self.id} - {self.member.first_name} {self.member.last_name}"

# ------------------------------
# MEMBER INVESTMENTS MODEL
# ------------------------------
class Investment(models.Model):
    member = models.ForeignKey("Member", on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    investment_date = models.DateTimeField(auto_now_add=True)
    return_rate = models.DecimalField(max_digits=5, decimal_places=2, default=5.0)  # Default 5% ROI
    maturity_date = models.DateField()

    def __str__(self):
        return f"Investment {self.id} - {self.member.first_name}"

    def calculate_return(self):
        """Calculate expected returns based on investment amount and return rate."""
        return (self.amount * self.return_rate) / 100

# ------------------------------
# TRANSACTIONS MODEL (Deposit, Withdrawal, Loan Repayment)
# ------------------------------
TRANSACTION_TYPES = [
    ('Deposit', 'Deposit'),
    ('Withdrawal', 'Withdrawal'),
    ('Loan Repayment', 'Loan Repayment'),
]

class Transaction(models.Model):
    member = models.ForeignKey("Member", on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_type} - {self.amount} by {self.member.first_name}"

# ------------------------------
# NOTIFICATIONS MODEL (Alerts, Reminders)
# ------------------------------
NOTIFICATION_TYPES = [
    ('Loan Approved', 'Loan Approved'),
    ('Payment Due', 'Payment Due'),
    ('Late Payment Penalty', 'Late Payment Penalty'),
    ('General', 'General'),
]

class Notification(models.Model):
    member = models.ForeignKey("Member", on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification {self.id} - {self.notification_type}"

# ------------------------------
# SUPPORT TICKETS MODEL
# ------------------------------
TICKET_STATUS = [
    ('Open', 'Open'),
    ('Resolved', 'Resolved'),
    ('Closed', 'Closed'),
]

class SupportTicket(models.Model):
    member = models.ForeignKey("Member", on_delete=models.CASCADE)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    status = models.CharField(max_length=10, choices=TICKET_STATUS, default='Open')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Ticket {self.id} - {self.subject} ({self.status})"



class ContactMessage(models.Model):
    id = models.AutoField(primary_key=True)  # ✅ Primary Key
    name = models.CharField(max_length=255)
    email = models.EmailField()
    subject = models.CharField(max_length=255)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)  # ✅ Auto timestamp

    def __str__(self):
        return f"Message from {self.name} - {self.subject}"

class Member(models.Model):
    member_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, unique=True)
    national_id = models.CharField(max_length=20, unique=True)
    address = models.TextField(blank=True, null=True)
    join_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=10, choices=[('Active', 'Active'), ('Inactive', 'Inactive')], default='Active'
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class MemberAccount(models.Model):
    account_number = models.CharField(max_length=8, unique=True, editable=False)
    member = models.OneToOneField(Member, on_delete=models.CASCADE)

    def __str__(self):
        return f"Account {self.account_number} - {self.member.first_name} {self.member.last_name}"


# Auto-generate an 8-digit account number
@receiver(post_save, sender=Member)
def create_member_account(sender, instance, created, **kwargs):
    if created:
        last_account = MemberAccount.objects.order_by('-account_number').first()
        
        if last_account and last_account.account_number.isdigit():
            new_account_number = str(int(last_account.account_number) + 1).zfill(8)  # Ensure 8-digit format
        else:
            new_account_number = "10000000"  # Start from 10000000

        MemberAccount.objects.create(
            member=instance,
            account_number=new_account_number
        )




class UserCredentials(models.Model):
    member_account_number = models.CharField(max_length=20, unique=True)
    password_hash = models.CharField(max_length=255)

    def __str__(self):
        return self.member_account_number

class LatePayment(models.Model):
    late_id = models.AutoField(primary_key=True)
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE)
    due_date = models.DateField()
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)
    days_late = models.IntegerField(default=0)
    penalty_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        self.days_late = (now().date() - self.due_date).days if self.due_date else 0
        self.penalty_amount = self.amount_due * 0.05 * self.days_late if self.days_late > 0 else 0
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Late Payment {self.late_id} - Loan {self.loan.loan_id}"



class Payment(models.Model):
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.id} - Loan {self.loan.id}"

