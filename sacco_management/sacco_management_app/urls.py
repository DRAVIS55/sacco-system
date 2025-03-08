"""
URL configuration for sacco_management project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views
from .views import apply_loan
from .views import make_repayment


    


urlpatterns = [
    path('make-repayment/', make_repayment, name='make_repayment'),
    path('auth_view/', views.auth_view, name='auth_view'),
    path('apply-loan/', apply_loan, name='apply_loan'),
    path('admin/', admin.site.urls),
    path('', views.home,name='home'),
    path('portfolio/', views.portfolio,name='portfolio'),
    path('services/', views.services,name='services'),
    path('register/', views.register,name='register'),
     path('about/', views.about,name='about'),
      path('faqs/', views.faq,name='faqs'),
      path('terms/', views.terms,name='terms'),
      path('privacy/', views.privacy,name='privacy'),
      path('advisory/', views.financiallyadvisory,name='advisory'),
      path('loans/', views.loan,name='loans'),
       path('banking/', views.banking,name='banking'),
       path('insurance/',views.insurance,name='insurance'),
       path('contact/',views.contact,name='contact'),
       path('login/',views.login_view,name='login'),
        path('userpanel/',views.userdashboard,name='userpanel'),
       path("setpassword/", views.setpassword, name="setpassword"),
         path("membership/", views.membership, name="membership"),
         path("savings/", views.savings, name="savings"),
         path("credits/", views.credits, name="credits"),
          path("investments/", views.investments, name="investments"),
           
]