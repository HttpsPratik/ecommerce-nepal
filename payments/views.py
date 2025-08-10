from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from orders.models import Order
from .models import Payment
from .esewa import ESewaPayment
from .khalti import KhaltiPayment

def payment_select(request, order_number):
    """Payment method selection"""
    order = get_object_or_404(Order, order_number=order_number)
    
    context = {
        'order': order,
    }
    return render(request, 'payments/payment_select.html', context)

def initiate_payment(request, order_number):
    """Process payment initiation"""
    if request.method == 'POST':
        order = get_object_or_404(Order, order_number=order_number)
        payment_method = request.POST.get('payment_method')
        
        # Create payment record
        payment = Payment.objects.create(
            order=order,
            payment_method=payment_method,
            amount=order.total_amount,
            status='pending'
        )
        
        if payment_method == 'esewa':
            return redirect('esewa_redirect', payment_id=payment.payment_id)
        elif payment_method == 'khalti':
            return redirect('khalti_redirect', payment_id=payment.payment_id)
        elif payment_method == 'cod':
            # Handle COD
            payment.status = 'pending'
            payment.save()
            order.status = 'confirmed'
            order.save()
            messages.success(request, 'Order confirmed! Pay on delivery.')
            return redirect('payment_success', payment_id=payment.payment_id)
    
    return redirect('payment_select', order_number=order_number)

def esewa_redirect(request, payment_id):
    """Redirect to eSewa"""
    payment = get_object_or_404(Payment, payment_id=payment_id)
    order = payment.order
    
    esewa = ESewaPayment()
    payment_data = esewa.prepare_payment_data(order, payment_id)
    
    context = {
        'payment_data': payment_data,
        'esewa_url': esewa.base_url,
        'order': order,
    }
    return render(request, 'payments/esewa_redirect.html', context)

def khalti_redirect(request, payment_id):
    """Redirect to Khalti"""
    payment = get_object_or_404(Payment, payment_id=payment_id)
    order = payment.order
    
    khalti = KhaltiPayment()
    success, response = khalti.initiate_payment(order, payment_id, request)
    
    if success and 'payment_url' in response:
        return redirect(response['payment_url'])
    else:
        messages.error(request, 'Payment initiation failed')
        return redirect('payment_select', order_number=order.order_number)

@csrf_exempt
def esewa_success(request):
    """Handle eSewa success"""
    transaction_uuid = request.GET.get('transaction_uuid')
    if transaction_uuid:
        try:
            payment = Payment.objects.get(payment_id=transaction_uuid)
            payment.status = 'completed'
            payment.save()
            
            order = payment.order
            order.payment_status = True
            order.status = 'confirmed'
            order.save()
            
            messages.success(request, 'Payment successful!')
            return redirect('payment_success', payment_id=payment.payment_id)
        except Payment.DoesNotExist:
            messages.error(request, 'Invalid payment')
    
    return redirect('home')

def payment_success(request, payment_id):
    """Payment success page"""
    payment = get_object_or_404(Payment, payment_id=payment_id)
    return render(request, 'payments/payment_success.html', {'payment': payment})