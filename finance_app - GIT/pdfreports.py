from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from io import BytesIO
import smtplib
from email.message import EmailMessage

def generate_pdf_report(username, df, kategoriler_toplam, aylik_toplam):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize = A4)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph(f"Kullanıcı: {username}", styles['Title']))
    story.append(Spacer(1,12))

    story.append(Paragraph("💰 Kategorilere Göre Toplam Gider:", styles['Heading2']))
    data = [["Kategori", "Toplam Tutar"]] + [[k, f"{v:.2f}₺"] for k, v in kategoriler_toplam.items()]
    story.append(Table(data))
    story.append(Spacer(1,12))

    story.append(Paragraph("📅 Aylık Gelir-Gider Özeti:", styles['Heading2']))
    aylik_data = [["Ay", "Gelir", "Gider"]] + [[ay, f"{row.get('Gelir', 0):.2f}₺", f"{row.get('Gider', 0):.2f}₺"] for ay, row in aylik_toplam.iterrows()]
    story.append(Table(aylik_data))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

def send_email(to_email, pdf_buffer, username):
    msg = EmailMessage()
    msg["Subject"] = "Kişisel Finans Raporu"
    msg["From"] = "your@email.com"
    msg["To"] = to_email
    msg.set_content(f"{username} kullanıcısına ait finans raporu ektedir.")

    msg.add_attachment(pdf_buffer.read(), maintype = 'application', subtype = 'pdf', filename = 'rapor.pdf')

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        #Gmail'e uygulama şifresi yazıp şifreyi alabilirsin. Bunun için iki adımlı doğrulamayı açmalısın!
        smtp.login("your@email.com", "Senin app şifren")
        smtp.send_message(msg)