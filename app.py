from flask import Flask, render_template, request
import fitz  # PyMuPDF
import os
import re

app = Flask(__name__)

UPLOAD_FOLDER = "samples"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# -------------------------------
# Extract text from PDF
# -------------------------------
def extract_text_from_pdf(pdf_path):
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text("text")
    return text


# -------------------------------
# Main credit card statement parser
# -------------------------------
def extract_details(text):
    clean_text = " ".join(text.split())

    # Try to detect issuer from text first
    issuer = detect_issuer(clean_text)

    # Parse using issuer-specific logic if possible
    details = parse_statement(clean_text, issuer)

    # Add bank/issuer name to results
    details["Bank / Issuer"] = issuer.title() if issuer else "Not Found"

    # Ensure all 6 keys exist
    final_keys = [
        "Bank / Issuer",
        "Card Variant",
        "Card Last 4 Digits",
        "Billing Period",
        "Payment Due Date",
        "Total Due",
    ]
    for k in final_keys:
        if k not in details:
            details[k] = "Not Found"

    return details


# -------------------------------
# Detect issuer name from text
# -------------------------------
def detect_issuer(text):
    issuers = [
        "American Express",
        "AXIS",
        "Axis Bank",
        "ICICI",
        "HDFC",
        "SBI",
        "KOTAK",
        "CANARA",
        "YES BANK",
        "CITI",
        "CHASE",
        "CAPITAL ONE",
        "DISCOVER",
    ]
    for issuer in issuers:
        if re.search(issuer, text, re.IGNORECASE):
            return issuer
    return "Unknown"


# -------------------------------
# Issuer-specific parsing logic
# -------------------------------
def parse_statement(text, issuer):
    details = {
        "Card Variant": "Not Found",
        "Card Last 4 Digits": "Not Found",
        "Billing Period": "Not Found",
        "Payment Due Date": "Not Found",
        "Total Due": "Not Found",
    }

    clean_text = " ".join(text.split())

    # Helper pattern for Payment Due Date (shared by all)
    due_date_pattern = r"Payment\s*Due\s*Date[:\s]*([0-9A-Za-z\s/]+?)(?=\s*(Total|New|Amount|Balance|$))"

    # -------------- American Express --------------
    if re.search("american express", issuer, re.IGNORECASE):
        variant = re.search(r"Card[:\s]+([A-Za-z\s]+)", clean_text)
        if variant:
            details["Card Variant"] = variant.group(1).strip()

        last4 = re.search(
            r"(?:\*{4}\s*\*{4}\s*\*{4}\s*(\d{4})|Card\s*Ending[:\s\*]+(\d{4}))",
            clean_text,
        )
        if last4:
            details["Card Last 4 Digits"] = next(g for g in last4.groups() if g)

        cycle = re.search(
            r"(?:Billing|Statement)\s*Period[:\s]*([0-9A-Za-z\s/]+)[–\-]\s*([0-9A-Za-z\s/]+)",
            clean_text,
        )
        if cycle:
            details["Billing Period"] = f"{cycle.group(1)} to {cycle.group(2)}"

        due = re.search(due_date_pattern, clean_text, re.IGNORECASE)
        if due:
            details["Payment Due Date"] = due.group(1).strip()

        total = re.search(
            r"(?:Total\s*Due|New\s*Balance)[:\s]*([$₹Rs\.0-9,]+)",
            clean_text,
            re.IGNORECASE,
        )
        if total:
            details["Total Due"] = total.group(1)

    # -------------- Axis Bank --------------
    elif re.search("axis", issuer, re.IGNORECASE):
        variant = re.search(r"Card\s*Type[:\s]*([A-Za-z0-9\s]+)", clean_text)
        if variant:
            details["Card Variant"] = variant.group(1).strip()

        last4 = re.search(r"XXXX\s*XXXX\s*XXXX\s*(\d{4})", clean_text)
        if last4:
            details["Card Last 4 Digits"] = last4.group(1)

        cycle = re.search(r"Statement\s*Period[:\s]*([0-9A-Za-z\s]+)\s*-\s*([0-9A-Za-z\s]+)", clean_text)
        if cycle:
            details["Billing Period"] = f"{cycle.group(1)} to {cycle.group(2)}"

        due = re.search(due_date_pattern, clean_text, re.IGNORECASE)
        if due:
            details["Payment Due Date"] = due.group(1)

        total = re.search(r"(?:Total\s*Amount\s*Due|Amount\s*Due)[:\s]*([$₹Rs\.0-9,]+)", clean_text)
        if total:
            details["Total Due"] = total.group(1)

    # -------------- HDFC --------------
    elif re.search("hdfc", issuer, re.IGNORECASE):
        last4 = re.search(r"(?:Card\s*No[:\s]*[0-9Xx\s]+(\d{4}))", clean_text)
        if last4:
            details["Card Last 4 Digits"] = last4.group(1)

        cycle = re.search(
            r"Billing\s*(Cycle|Period)[:\s]*([0-9A-Za-z\s]+)[–\-]\s*([0-9A-Za-z\s]+)",
            clean_text,
        )
        if cycle:
            details["Billing Period"] = f"{cycle.group(2)} to {cycle.group(3)}"
        else:
            stmt_date = re.search(r"Statement\s*Date[:\s]*([0-9\/A-Za-z]+)", clean_text)
            if stmt_date:
                details["Billing Period"] = stmt_date.group(1)

        due = re.search(due_date_pattern, clean_text, re.IGNORECASE)
        if due:
            details["Payment Due Date"] = due.group(1)

        total = re.search(r"(?:Total\s*(Amount\s*)?Dues?)[:\s]*([$₹Rs\.0-9,]+)", clean_text)
        if total:
            details["Total Due"] = total.group(2)

    # -------------- ICICI --------------
    elif re.search("icici", issuer, re.IGNORECASE):
        variant = re.search(r"Card\s*Type[:\s]*([A-Za-z\s]+)", clean_text)
        if variant:
            details["Card Variant"] = variant.group(1).strip()

        last4 = re.search(r"XXXX\s*XXXX\s*XXXX\s*(\d{4})", clean_text)
        if last4:
            details["Card Last 4 Digits"] = last4.group(1)

        cycle = re.search(r"Statement\s*Period[:\s]*([0-9A-Za-z\s]+)\s*[-–]\s*([0-9A-Za-z\s]+)", clean_text)
        if cycle:
            details["Billing Period"] = f"{cycle.group(1)} to {cycle.group(2)}"

        due = re.search(due_date_pattern, clean_text, re.IGNORECASE)
        if due:
            details["Payment Due Date"] = due.group(1)

        total = re.search(r"(?:Total\s*Amount\s*Due|New\s*Balance)[:\s]*([$₹Rs\.0-9,]+)", clean_text)
        if total:
            details["Total Due"] = total.group(1)

    # -------------- SBI --------------
    elif re.search("sbi", issuer, re.IGNORECASE):
        variant = re.search(r"Card\s*Type[:\s]*([A-Za-z\s]+)", clean_text)
        if variant:
            details["Card Variant"] = variant.group(1).strip()

        last4 = re.search(r"XXXX\s*XXXX\s*XXXX\s*(\d{4})", clean_text)
        if last4:
            details["Card Last 4 Digits"] = last4.group(1)

        cycle = re.search(r"Statement\s*Period[:\s]*([0-9A-Za-z\s]+)\s*[-–]\s*([0-9A-Za-z\s]+)", clean_text)
        if cycle:
            details["Billing Period"] = f"{cycle.group(1)} to {cycle.group(2)}"

        due = re.search(due_date_pattern, clean_text, re.IGNORECASE)
        if due:
            details["Payment Due Date"] = due.group(1)

        total = re.search(r"(?:Total\s*Amount\s*Due|New\s*Balance)[:\s]*([$₹Rs\.0-9,]+)", clean_text)
        if total:
            details["Total Due"] = total.group(1)

    # -------------- Chase Bank --------------
    elif re.search("chase", issuer, re.IGNORECASE):
        last4 = re.search(r"(?:Account\s*Number|Card\s*No\.?)[:\s\-]*X{0,4}\s*X{0,4}\s*X{0,4}\s*(\d{4})", clean_text)
        if last4:
            details["Card Last 4 Digits"] = last4.group(1)

        cycle = re.search(r"(?:Opening\/Closing\s*Date|Billing\s*Period)[:\s]*([0-9\/A-Za-z]+)\s*[-–]\s*([0-9\/A-Za-z]+)", clean_text)
        if cycle:
            details["Billing Period"] = f"{cycle.group(1)} to {cycle.group(2)}"

        due = re.search(due_date_pattern, clean_text, re.IGNORECASE)
        if due:
            details["Payment Due Date"] = due.group(1)

        total = re.search(r"(?:New\s*Balance|Total\s*Due|Amount\s*Payable)[:\s]*([$₹Rs\.0-9,]+)", clean_text)
        if total:
            details["Total Due"] = total.group(1)

    # -------------- Generic fallback --------------
    else:
        last4 = re.search(r"(?:XXXX\s*XXXX\s*XXXX\s*(\d{4})|Card\s*Ending[:\s\*]+(\d{4}))", clean_text)
        if last4:
            details["Card Last 4 Digits"] = next(g for g in last4.groups() if g)

        cycle = re.search(r"(?:Billing|Statement)\s*(Period|Cycle)[:\s]*([0-9A-Za-z\s]+)[–\-]\s*([0-9A-Za-z\s]+)", clean_text)
        if cycle:
            details["Billing Period"] = f"{cycle.group(2)} to {cycle.group(3)}"

        due = re.search(due_date_pattern, clean_text, re.IGNORECASE)
        if due:
            details["Payment Due Date"] = due.group(1)

        total = re.search(r"(?:Total\s*(Amount)?\s*Due|New\s*Balance)[:\s]*([$₹Rs\.0-9,]+)", clean_text)
        if total:
            details["Total Due"] = total.group(2)

    return details


# -------------------------------
# Flask Routes
# -------------------------------
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