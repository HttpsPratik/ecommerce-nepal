from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from products.cart import Cart
from .models import Order, OrderItem

def checkout(request):
    """Checkout process"""
    cart = Cart(request)
    
    if len(cart) == 0:
        messages.error(request, 'Your cart is empty!')
        return redirect('cart_detail')
    
    if request.method == 'POST':
        try:
            # Create order
            order = Order.objects.create(
                user=request.user if request.user.is_authenticated else None,
                email=request.POST.get('email', ''),
                first_name=request.POST.get('first_name', ''),
                last_name=request.POST.get('last_name', ''),
                phone=request.POST.get('phone', ''),
                address=request.POST.get('address', ''),
                city=request.POST.get('city', ''),
                postal_code=request.POST.get('postal_code', ''),
                total_amount=cart.get_total_price(),
                payment_method=request.POST.get('payment_method', 'cod'),
                notes=request.POST.get('notes', '')
            )
            
            # Create order items
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    price=item['price'],
                    quantity=item['quantity']
                )
            
            # Clear cart
            cart.clear()
            
            # Handle payment method
            payment_method = request.POST.get('payment_method', 'cod')
            
            if payment_method == 'cod':
                order.status = 'confirmed'
                order.save()
                messages.success(request, f'Order #{str(order.order_number)[:8]}... placed successfully! You will pay on delivery.')
                return redirect('order_created', order_number=order.order_number)
            elif payment_method in ['esewa', 'khalti']:
                # For now, simulate payment success
                order.payment_status = True
                order.status = 'confirmed'
                order.save()
                messages.success(request, f'{payment_method.title()} payment successful! Order confirmed.')
                return redirect('order_created', order_number=order.order_number)
            
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
            return redirect('checkout')
    
    context = {
        'cart': cart,
        'cart_items': cart.get_cart_items(),
    }
    return render(request, 'orders/checkout.html', context)

def order_created(request, order_number):
    """Order confirmation page"""
    order = get_object_or_404(Order, order_number=order_number)
    return render(request, 'orders/order_created.html', {'order': order})

@login_required
def order_list(request):
    """User's order history"""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/order_list.html', {'orders': orders})

@login_required
def order_detail(request, order_number):
    """Individual order details"""
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    return render(request, 'orders/order_detail.html', {'order': order})