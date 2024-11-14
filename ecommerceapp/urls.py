from django.urls import path,include
from ecommerceapp import views

urlpatterns = [
    path('',views.index,name="index"),
    path('contact',views.contact,name="contact"),
    path('about',views.about,name="about"),
    path('blog',views.blog,name="blog"),
    path('checkout/',views.checkout,name="Checkout"),

    path('paypal/', include('paypal.standard.ipn.urls')),
    path('payment-success/', views.payment_success, name='payment_success'),
    path('payment-failed/', views.payment_failed, name='payment_failed'),

    
]

