from django.shortcuts import render, redirect
from ecommerceapp.models import Contact, Product, Orders, OrderUpdate
from django.contrib import messages
from math import ceil
from django.urls import reverse
from paypal.standard.forms import PayPalPaymentsForm
from django.conf import settings
from paypal.standard.models import ST_PP_COMPLETED
from paypal.standard.ipn.signals import valid_ipn_received
from django.dispatch import receiver
import uuid

def index(request):
    allProds = []
    catprods = Product.objects.values('catigory', 'id')
    cats = {item['catigory'] for item in catprods}
    for cat in cats:
        prod = Product.objects.filter(catigory=cat)
        n = len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        allProds.append([prod, range(1, nSlides), nSlides])
    params = {'allProds': allProds}
    return render(request, "index.html", params)

def contact(request):
    if request.method == "POST":
        name = request.POST['name']
        email = request.POST['email']
        desc = request.POST['desc']
        pnumber = request.POST['pnumber']
        myquery = Contact(name=name, email=email, desc=desc, phoneno=pnumber)
        myquery.save()
        messages.info(request, "We will contact you soon!")
    return render(request, "contact.html")

def about(request):
    return render(request, "about.html")

def blog(request):
    return render(request, "blog.html")

def checkout(request):
    if request.method == "POST":
        items_json = request.POST.get('itemsJson', '')
        name = request.POST.get('name', '')
        amount = request.POST.get('amt', '0')
        email = request.POST.get('email', '')
        address1 = request.POST.get('address1', '')
        address2 = request.POST.get('address2', '')
        city = request.POST.get('city', '')
        state = request.POST.get('state', '')
        zip_code = request.POST.get('zip_code', '')
        phone = request.POST.get('phone', '')
        payment_method = request.POST.get('payment_method', 'COD')

        try:
            amount = float(amount)
        except ValueError:
            amount = 0

        order = Orders(
            items_json=items_json,
            name=name,
            amount=amount,
            email=email,
            address1=address1,
            address2=address2,
            city=city,
            state=state,
            zip_code=zip_code,
            phone=phone
        )
        order.save()

        if payment_method == "COD":
            update = OrderUpdate(
                order_id=order.order_id,
                update_desc="The order has been placed and will be paid via Cash on Delivery"
            )
            update.save()
            thank = True
            return render(request, 'checkout.html', {'thank': thank, 'id': order.order_id})

        elif payment_method == "PayPal":
            host = request.get_host()
            paypal_dict = {
                'business': settings.PAYPAL_RECEIVER_EMAIL,
                'amount': f"{amount:.2f}",
                'item_name': 'Online Order',
                'invoice': str(order.order_id),
                'currency_code': 'USD',
                'notify_url': f'https://{host}{reverse("paypal-ipn")}',
                'return_url': f'https://{host}{reverse("payment_success")}',
                'cancel_return': f'https://{host}{reverse("payment_failed")}',
            }
            paypal_form = PayPalPaymentsForm(initial=paypal_dict)

            update = OrderUpdate(
                order_id=order.order_id,
                update_desc="The order has been placed and is pending PayPal payment"
            )
            update.save()

            return render(request, 'paypal_payment.html', {
                'order': order,
                'paypal_form': paypal_form,
                'amount': amount
            })

    return render(request, 'checkout.html')

def payment_success(request):
    messages.success(request, "Your payment was successful!")
    return render(request, "payment_success.html")

def payment_failed(request):
    messages.error(request, "Your payment was cancelled or failed.")
    return render(request, "payment_failed.html")

@receiver(valid_ipn_received)
def paypal_payment_notification(sender, **kwargs):
    ipn_obj = sender
    if ipn_obj.payment_status == ST_PP_COMPLETED:
        try:
            order = Orders.objects.get(order_id=ipn_obj.invoice)
            order.payment_status = 'Completed'
            order.save()

            update = OrderUpdate(
                order_id=order.order_id,
                update_desc="The order payment has been completed via PayPal."
            )
            update.save()

        except Orders.DoesNotExist:
            pass
