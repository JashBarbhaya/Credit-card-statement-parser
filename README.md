# Credit Card Statement Parser

A **Python Flask application** that extracts key information from credit card PDF statements for multiple banks including **ICICI, HDFC, AXIS, SBI, and KOTAK**. It retrieves essential details such as Bank Name, Cardholder Name, Card Last 4 Digits, Billing Cycle, Payment Due Date, and Total Amount Due.  

---

## Features

- Extracts critical details from PDF credit card statements  
- Supports multiple banks and PDF formats  
- Robust extraction for Total Amount Due, including ₹ symbol  
- Unicode support with DejaVuSans font  
- Web interface for selecting PDFs and displaying results  
- Sample PDFs included with dummy transactions for testing  

---

## Tech Stack

- **Python**  
- **Flask**  
- **PyMuPDF (fitz)**  
- **ReportLab** (for PDF generation)  

---

## Demo Screenshots

### Homepage
![Homepage](screenshots/home.png)

### Parsed Result
![Parsed Result](screenshots/result.png)

---

## Installation

1. **Clone the repository:**
```bash
git clone https://github.com/<your-username>/credit-card-statement-parser.git
cd credit-card-statement-parser
