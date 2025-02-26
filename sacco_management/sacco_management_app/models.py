from django.db import models
from django.contrib.auth.models import User
from datetime import date
from django.utils.timezone import now
# Create your models here.
from django.contrib.auth.hashers import make_password
from django.dispatch import receiver
from django.db.models.signals import post_save

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




class Loan(models.Model):
    loan_id = models.AutoField(primary_key=True)
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    start_date = models.DateField()
    due_date = models.DateField()
    status = models.CharField(max_length=15, choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Paid', 'Paid')])

    def __str__(self):
        return f"Loan {self.loan_id} - {self.member.first_name}"

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

