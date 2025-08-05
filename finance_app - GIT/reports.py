from fpdf import FPDF
import smtplib
import os
import pandas as pd
from email.message import EmailMessage
from db import get_transactions

def create_pdf(username):
    df = get_transactions(username)
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size= 12)
    pdf.cell(200, 10, txt= f"{username} - Kişisel Finans Raporu", ln= 1, align= 'C')
    pdf.ln(10)

    if df.empty:
        pdf.cell(200, 10, txt = "Hiç veri bulunamadı.", ln= 1)
    else:
        col_widths = [30, 20, 40, 30, 60]
        headers = df.columns.tolist()

        for i, header in enumerate(headers):
            pdf.cell(col_widths[i], 10, txt = header, border= 1)

        pdf.ln()

    pdf_path = f"{username}_rapor.pdf"
    pdf.output(pdf_path)
    return pdf_path

def send_email(receiver_email, subject, body, attachment_path):
    sender_email = "huseyinccolakk@gmail.com"
    sender_password = "rmmv ndas inqa efrp"

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = receiver_email

    with open(attachment_path, "rb") as f:
        file_data = f.read()
        file_name = os.path.basename(attachment_path)

    msg.add_attachment(file_data, maintype = 'application', subtype = 'octet-stream', filename = file_name)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(sender_email, sender_password)
        smtp.send_message(msg)