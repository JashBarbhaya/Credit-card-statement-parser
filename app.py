from flask import Flask, render_template, request
import fitz  # PyMuPDF
import os
import re

app = Flask(__name__)

UPLOAD_FOLDER = "samples"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# ----------- Function to extract text from PDF -----------
def extract_text_from_pdf(pdf_path):
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text("text")
    return text

# ----------- Extract key data points (generic & robust) -----------
def extract_details(text):
    details = {}

    # Normalize text: remove extra spaces and join lines
    clean_text = " ".join(text.split())

    # Bank Name
    bank_match = re.search(r"([A-Za-z &]+(?:Bank|Credit Card))", clean_text, re.IGNORECASE)
    details["Bank Name"] = bank_match.group(1).strip() if bank_match else "Not Found"

    # Cardholder Name
    name_match = re.search(r"(Cardholder Name|Name on Card)[:\s]*(.*?)\s(?:Card|Billing|Payment|Total)", clean_text, re.IGNORECASE)
    details["Cardholder Name"] = name_match.group(2).strip() if name_match else "Not Found"

    # Card Last 4 Digits
    card_match = re.search(r"(?:XXXX\s*XXXX\s*XXXX\s*|Card Number[:\s]*)(\d{4})", clean_text)
    details["Card Last 4 Digits"] = card_match.group(1) if card_match else "Not Found"

    # Billing Cycle
    cycle_match = re.search(r"(Billing Cycle|Statement Period)[:\s]*([\d/]+)\s*[-to]+\s*([\d/]+)", clean_text, re.IGNORECASE)
    details["Billing Cycle"] = f"{cycle_match.group(2)} to {cycle_match.group(3)}" if cycle_match else "Not Found"

    # Payment Due Date
    due_match = re.search(r"(Payment Due Date|Due Date)[:\s]*([\d/]+)", clean_text, re.IGNORECASE)
    details["Payment Due Date"] = due_match.group(2) if due_match else "Not Found"

    # Total Amount Due - very flexible
    total_match = re.search(
        r"(Total\s*(Amount)?\s*Due|Amount\s*Due|New\s*Balance)\s*[:]*\s*([₹]?\s*[\d,]+\.\d{2})",
        clean_text,
        re.IGNORECASE
    )
    details["Total Due"] = total_match.group(3).replace(" ", "") if total_match else "Not Found"

    return details
# ----------- Routes -----------
@app.route("/")
def home():
    pdf_files = [f for f in os.listdir(app.config["UPLOAD_FOLDER"]) if f.endswith(".pdf")]
    return render_template("index.html", pdfs=pdf_files)

@app.route("/parse", methods=["POST"])
def parse_file():
    selected_pdf = request.form.get("pdf_name")
    if not selected_pdf:
        return "No PDF selected", 400

    pdf_path = os.path.join(app.config["UPLOAD_FOLDER"], selected_pdf)
    text = extract_text_from_pdf(pdf_path)
    data = extract_details(text)

    return render_template("result.html", pdf_name=selected_pdf, data=data)

if __name__ == "__main__":
    app.run(debug=True)
