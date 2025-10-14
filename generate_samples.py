from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import letter
import os

os.makedirs("samples", exist_ok=True)

# Register a Unicode font
pdfmetrics.registerFont(TTFont('DejaVu', 'DejaVuSans.ttf'))

samples = [
    {"bank": "ICICI Bank", "name": "Emma Watson", "card": "4321", "cycle": "01/10/2025 - 31/10/2025", "due": "10/11/2025", "total": "₹9,750.50"},
    {"bank": "HDFC Bank", "name": "Liam Brown", "card": "8765", "cycle": "01/10/2025 - 31/10/2025", "due": "12/11/2025", "total": "₹14,320.00"},
    {"bank": "AXIS Bank", "name": "Olivia Green", "card": "2109", "cycle": "01/10/2025 - 31/10/2025", "due": "15/11/2025", "total": "₹7,890.25"},
    {"bank": "SBI Bank", "name": "Noah White", "card": "6543", "cycle": "01/10/2025 - 31/10/2025", "due": "18/11/2025", "total": "₹11,500.00"},
    {"bank": "KOTAK Bank", "name": "Sophia Black", "card": "0987", "cycle": "01/10/2025 - 31/10/2025", "due": "20/11/2025", "total": "₹16,750.75"}
]

for sample in samples:
    file_name = f"samples/{sample['bank'].split()[0].lower()}_sample2.pdf"
    c = canvas.Canvas(file_name, pagesize=letter)
    c.setFont("DejaVu", 12)  # Use Unicode font

    # Write PDF content
    c.drawString(50, 700, f"Bank: {sample['bank']}")
    c.drawString(50, 680, f"Cardholder Name: {sample['name']}")
    c.drawString(50, 660, f"Card Number: XXXX XXXX XXXX {sample['card']}")
    c.drawString(50, 640, f"Billing Cycle: {sample['cycle']}")
    c.drawString(50, 620, f"Payment Due Date: {sample['due']}")
    c.drawString(50, 600, f"Total Amount Due: {sample['total']}")

    # Dummy transactions
    y = 580
    for i in range(1, 4):
        c.drawString(50, y, f"Transaction {i}: 01/09/2025 - Store {i} - ₹{100*i}")
        y -= 20

    c.save()

print("5 sample PDFs created with proper Rupee symbol!")
