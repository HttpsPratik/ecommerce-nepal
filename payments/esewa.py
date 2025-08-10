import hashlib
import hmac
from django.conf import settings
from django.urls import reverse

class ESewaPayment:
    def __init__(self):
        self.merchant_code = getattr(settings, 'ESEWA_MERCHANT_CODE', 'EPAYTEST')
        self.secret_key = getattr(settings, 'ESEWA_SECRET_KEY', '8gBm/:&EnhH.1/q')
        self.base_url = "https://uat.esewa.com.np/epay/main"  # Test environment
    
    def generate_signature(self, message):
        """Generate HMAC signature for eSewa"""
        try:
            signature = hmac.new(
                self.secret_key.encode('utf-8'),
                message.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            return signature
        except Exception as e:
            print(f"Error generating signature: {e}")
            return None
    
    def prepare_payment_data(self, order, payment_id):
        """Prepare payment data for eSewa"""
        try:
            total_amount = str(int(order.total_amount))
            transaction_uuid = str(payment_id)
            product_code = self.merchant_code
            
            # Create signature message
            message = f"total_amount={total_amount},transaction_uuid={transaction_uuid},product_code={product_code}"
            signature = self.generate_signature(message)
            
            payment_data = {
                'amount': total_amount,
                'total_amount': total_amount,
                'transaction_uuid': transaction_uuid,
                'product_code': product_code,
                'product_service_charge': '0',
                'product_delivery_charge': '0',
                'success_url': 'http://127.0.0.1:8000/payments/esewa/success/',
                'failure_url': 'http://127.0.0.1:8000/payments/esewa/failure/',
                'signed_field_names': 'total_amount,transaction_uuid,product_code',
                'signature': signature,
            }
            
            return payment_data
            
        except Exception as e:
            print(f"Error preparing eSewa payment: {e}")
            return None