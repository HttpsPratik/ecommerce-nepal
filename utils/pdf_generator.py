import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.lib.colors import black, blue, gray
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from django.http import HttpResponse
from django.conf import settings
import qrcode
from PIL import Image
import logging

logger = logging.getLogger(__name__)

class InvoicePDFGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.page_width, self.page_height = A4
    
    def generate_invoice(self, order, payment=None):
        """Generate PDF invoice for an order"""
        try:
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1*inch)
            
            # Container for the 'Flowable' objects
            elements = []
            
            # Add header
            elements.extend(self._create_header(order))
            
            # Add order details
            elements.extend(self._create_order_details(order))
            
            # Add items table
            elements.extend(self._create_items_table(order))
            
            # Add totals
            elements.extend(self._create_totals_section(order))
            
            # Add payment info if available
            if payment:
                elements.extend(self._create_payment_section(payment))
            
            # Add footer
            elements.extend(self._create_footer(order))
            
            # Build PDF
            doc.build(elements)
            
            buffer.seek(0)
            logger.info(f"PDF invoice generated for order {order.get_short_order_number()}")
            return buffer
            
        except Exception as e:
            logger.error(f"Error generating PDF invoice: {e}")
            return None
    
    def _create_header(self, order):
        """Create invoice header"""
        elements = []
        
        # Company header
        header_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=blue
        )
        
        elements.append(Paragraph("NEPAL STORE", header_style))
        elements.append(Paragraph("Your Trusted Online Shopping Destination", 
                                 self.styles['Normal']))
        elements.append(Spacer(1, 20))
        
        # Invoice title
        invoice_style = ParagraphStyle(
            'InvoiceTitle',
            parent=self.styles['Heading2'],
            fontSize=18,
            alignment=TA_CENTER,
            spaceAfter=20
        )
        elements.append(Paragraph("INVOICE", invoice_style))
        
        return elements
    
    def _create_order_details(self, order):
        """Create order details section"""
        elements = []
        
        # Create two-column layout for order and customer details
        order_data = [
            ['Order Information', 'Customer Information'],
            [f'Order #: {order.get_short_order_number()}', f'Name: {order.get_full_name()}'],
            [f'Date: {order.created_at.strftime("%B %d, %Y")}', f'Email: {order.email}'],
            [f'Status: {order.get_status_display()}', f'Phone: {order.phone}'],
            [f'Payment: {order.get_payment_method_display()}', f'Address: {order.address}'],
            ['', f'City: {order.city}, {order.postal_code}']
        ]
        
        table = Table(order_data, colWidths=[3*inch, 3*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (1, 0), gray),
            ('TEXTCOLOR', (0, 0), (1, 0), black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, black),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _create_items_table(self, order):
        """Create items table"""
        elements = []
        
        # Table header
        data = [['Product', 'Price', 'Quantity', 'Total']]
        
        # Add items
        for item in order.items.all():
            data.append([
                item.product.name,
                f'Rs. {item.price}',
                str(item.quantity),
                f'Rs. {item.get_cost()}'
            ])
        
        table = Table(data, colWidths=[3*inch, 1.5*inch, 1*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), gray),
            ('TEXTCOLOR', (0, 0), (-1, 0), black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),  # Product names left-aligned
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, black),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _create_totals_section(self, order):
        """Create totals section"""
        elements = []
        
        subtotal = order.total_amount / 1.13  # Remove tax
        tax = order.total_amount - subtotal
        
        totals_data = [
            ['Subtotal:', f'Rs. {subtotal:.2f}'],
            ['Tax (13%):', f'Rs. {tax:.2f}'],
            ['Shipping:', 'FREE' if order.total_amount >= 1000 else 'Rs. 100'],
            ['Total:', f'Rs. {order.total_amount}']
        ]
        
        totals_table = Table(totals_data, colWidths=[4*inch, 2*inch])
        totals_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LINEBELOW', (0, -1), (-1, -1), 1, black),
        ]))
        
        elements.append(totals_table)
        elements.append(Spacer(1, 30))
        
        return elements
    
    def _create_payment_section(self, payment):
        """Create payment information section"""
        elements = []
        
        if payment.is_successful():
            payment_data = [
                ['Payment Information'],
                [f'Payment ID: {payment.get_short_payment_id()}'],
                [f'Method: {payment.get_payment_method_display()}'],
                [f'Status: PAID'],
                [f'Date: {payment.completed_at.strftime("%B %d, %Y %I:%M %p") if payment.completed_at else "Pending"}']
            ]
            
            payment_table = Table(payment_data, colWidths=[6*inch])
            payment_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, 0), gray),
                ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, black),
            ]))
            
            elements.append(payment_table)
            elements.append(Spacer(1, 20))
        
        return elements
    
    def _create_footer(self, order):
        """Create invoice footer"""
        elements = []
        
        footer_text = """
        <para align=center>
        <b>Thank you for shopping with Nepal Store!</b><br/>
        For any queries, contact us at support@nepalstore.com or +977-1-4444444<br/>
        <i>This is a computer generated invoice and does not require signature.</i>
        </para>
        """
        
        elements.append(Spacer(1, 30))
        elements.append(Paragraph(footer_text, self.styles['Normal']))
        
        return elements

def generate_invoice_response(order, payment=None):
    """Generate HTTP response with PDF invoice"""
    generator = InvoicePDFGenerator()
    buffer = generator.generate_invoice(order, payment)
    
    if buffer:
        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        filename = f'invoice-{order.get_short_order_number()}.pdf'
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    else:
        return HttpResponse('Error generating PDF', status=500)