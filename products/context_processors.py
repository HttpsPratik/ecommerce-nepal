from .cart import Cart

def cart(request):
    """Make cart available in all templates"""
    try:
        cart_obj = Cart(request)
        return {'cart': cart_obj}
    except Exception as e:
        print(f"Cart context processor error: {e}")
        return {'cart': None}