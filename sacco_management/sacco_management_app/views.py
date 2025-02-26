from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.hashers import make_password
from django.http import HttpResponse
from .models import UserCredentials, Member  # Ensure Member model is imported
from django.contrib.auth.hashers import check_password
from .models import UserCredentials,MemberAccount
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User  # Import Django's User model


# Create your views here.
def home(request):
    return render(request,'index.html')

def portfolio(request):
    return render(request,'portfolio-details.html')

def services(request):
    return render(request,'service-details.html')


def register(request):
    if request.method == "POST":
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        email = request.POST["email"]
        phone = request.POST["phone"]
        national_id = request.POST["national_id"]
        address = request.POST["address"]

        # Check if phone number already exists
        if Member.objects.filter(phone=phone).exists():
            messages.error(request, "This phone number is already registered.")
            return redirect("register")

        # Check if email already exists
        if Member.objects.filter(email=email).exists():
            messages.error(request, "This email is already registered.")
            return redirect("register")

        # Check if national ID already exists
        if Member.objects.filter(national_id=national_id).exists():
            messages.error(request, "This National ID is already registered.")
            return redirect("register")

        new_member = Member.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            national_id=national_id,
            address=address
        )

        # Fetch the newly created account number
        member_account = MemberAccount.objects.get(member=new_member)

        return render(request, "accountconfirmation.html", {"account_number": member_account.account_number})

    return render(request, "register.html")


    


def about(request):
    return render(request,'about.html')

def faq(request):
    return render(request,'faqs.html')

def terms(request):
    return render(request,'terms.html')

def privacy(request):
    return render(request,'privacy.html')

def financiallyadvisory(request):
    return render(request,'financialadvisory.html')

def loan(request):
    return render(request,'loanproduct.html')

def banking(request):
    return render(request,'banking.html')

def insurance(request):
    return render(request,'insurance.html')

def contact(request):
    return render(request,'contact.html')

def login_view(request):
    if request.method == "POST":
        account_number = request.POST.get('account_number', '').strip()
        password = request.POST.get('password', '').strip()

        if not account_number or not password:
            messages.error(request, "Account number and password are required.")
            return redirect('login')

        try:
            member_account = MemberAccount.objects.get(account_number=account_number)
            member = member_account.member
        except MemberAccount.DoesNotExist:
            messages.error(request, "Invalid account number. Please try again.")
            return redirect('login')

        # Authenticate using email (since Django User model uses username as email)
        user = authenticate(request, username=member.email, password=password)
        if user is not None:
            login(request, user)
            request.session['account_number'] = account_number  # Store account number in session
            return redirect('userpanel')
        else:
            messages.error(request, "Invalid password. Please try again.")
            return redirect('login')

    return render(request, 'login.html')



@login_required(login_url='login')
def userdashboard(request):
    account_number = request.session.get('account_number', None)

    if not account_number:
        messages.error(request, "Session expired. Please log in again.")
        return redirect('login')

    try:
        member_account = MemberAccount.objects.get(account_number=account_number)
        member = member_account.member
    except MemberAccount.DoesNotExist:
        messages.error(request, "Your account details are missing. Please contact support.")
        return redirect('error_page')

    return render(request, 'userdashboard.html', {
        'member': member,
        'member_account': member_account
    })

def setpassword(request):
    if request.method == "POST":
        account_number = request.POST["account_number"].strip()
        password = request.POST["password"].strip()
        confirm_password = request.POST["confirm_password"].strip()

        if password != confirm_password:
            return render(request, "setpassword.html", {"error": "Passwords do not match"})

        # Check if the MemberAccount exists
        try:
            member_account = MemberAccount.objects.get(account_number=account_number)
            member = member_account.member
        except MemberAccount.DoesNotExist:
            return render(request, "setpassword.html", {"error": "Account number not found"})

        # Create or update a Django User for authentication
        user, created = User.objects.get_or_create(username=member.email, defaults={
            "email": member.email,
            "first_name": member.first_name,
            "last_name": member.last_name,
            "password": make_password(password),  # Hash password before saving
        })

        if not created:
            user.password = make_password(password)  # Update password if user exists
            user.save()

        messages.success(request, "Password set successfully! You can now log in.")
        return redirect("login")

    return render(request, "setpassword.html")
