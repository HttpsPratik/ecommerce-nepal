import requests
from django.conf import settings

class KhaltiPayment:
    def __init__(self):
        self.public_key = getattr(settings, 'KHALTI_PUBLIC_KEY', 'test_public_key_dc74e0fd57cb46cd93832aee0a390234')
        self.secret_key = getattr(settings, 'KHALTI_SECRET_KEY', 'test_secret_key_f59e8b7d18b4499ca40f68195a846e9b')
        self.base_url = "https://khalti.com/api/v2/"
    
    def initiate_payment(self, order, payment_id, request):
        """Initiate Khalti payment"""
        try:
            url = f"{self.base_url}epayment/initiate/"
            
            headers = {
                'Authorization': f'Key {self.secret_key}',
                'Content-Type': 'application/json',
            }
            
            # Amount in paisa (multiply by 100)
            amount_in_paisa = int(order.total_amount * 100)
            
            data = {
                "return_url": "http://127.0.0.1:8000/payments/khalti/callback/",
                "website_url": "http://127.0.0.1:8000/",
                "amount": amount_in_paisa,
                "purchase_order_id": str(payment_id),
                "purchase_order_name": f"Order {str(order.order_number)[:8]}",
                "customer_info": {
                    "name": order.get_full_name(),
                    "email": order.email,
                    "phone": order.phone
                }
            }
            
            response = requests.post(url, json=data, headers=headers, timeout=30)
            
            if response.status_code == 200:
                return True, response.json()
            else:
                return False, "Payment initiation failed"
                
        except Exception as e:
            print(f"Khalti error: {e}")
            return False, str(e)