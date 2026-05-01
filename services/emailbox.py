import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os
from models.models import fullregistration

load_dotenv()
GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")

def _send(to_email: str, subject: str, html: str):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = GMAIL_USER
    msg["To"]      = to_email
    msg.attach(MIMEText(html, "html"))
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        server.sendmail(GMAIL_USER, to_email, msg.as_string())
        print(f"Email sent to {to_email}")


# ─────────────────────────────────────────────
# 1. PENDING — sent right after registration
#    No transaction code yet shown to customer
# ─────────────────────────────────────────────
def email_pending(data: fullregistration, trip_name: str, transaction_code: str):
    html = f"""
    <!DOCTYPE html><html><head><style>
      body {{ font-family: 'Segoe UI', Arial, sans-serif; background:#f5f5f5; margin:0; padding:0; }}
      .wrap {{ max-width:600px; margin:40px auto; background:#fff; border-radius:12px; overflow:hidden; border:1px solid #e0e0e0; }}
      .header {{ background:#1a73e8; padding:32px; text-align:center; }}
      .header h1 {{ color:#fff; margin:0; font-size:24px; }}
      .header p {{ color:#cce0ff; margin:8px 0 0; font-size:14px; }}
      .body {{ padding:32px; color:#333; line-height:1.7; }}
      .status-box {{ background:#fff8e1; border-left:4px solid #f9a825;
                     padding:16px 20px; border-radius:8px; margin:24px 0; }}
      .status-box p {{ margin:0; font-size:15px; color:#5f4b00; }}
      .code-box {{ background:#f0f7ff; border:1px dashed #1a73e8; padding:20px;
                   text-align:center; border-radius:10px; margin:24px 0; }}
      .code-box span {{ display:block; font-size:12px; color:#666; margin-bottom:6px; }}
      .code-box strong {{ font-size:22px; color:#1a73e8; letter-spacing:2px; }}
      .footer {{ background:#f1f3f4; padding:20px; text-align:center; font-size:12px; color:#888; }}
    </style></head><body>
    <div class="wrap">
      <div class="header">
        <h1>Reservation Received</h1>
        <p>We have your request — hang tight!</p>
      </div>
      <div class="body">
        <p>Dear <strong>{data.fullname}</strong>,</p>
        <p>Thank you for your interest in <strong>{trip_name}</strong>. We have received your reservation request and it is currently <strong>pending review</strong> by our team.</p>
        <div class="status-box">
          <p>⏳ <strong>Status: Pending</strong> — Our team will review your booking shortly. You will receive a confirmation email once it is approved.</p>
        </div>
        <div class="code-box">
          <span>Your Transaction Code (for reference)</span>
          <strong>{transaction_code}</strong>
        </div>
        <p>If you have any questions in the meantime, feel free to contact us.</p>
        <p>Best regards,<br><strong>The Travel Team</strong></p>
      </div>
      <div class="footer"><p>This is an automated message. Please do not reply directly to this email.</p></div>
    </div>
    </body></html>"""
    _send(data.email, f"Reservation Received — {trip_name}", html)


# ─────────────────────────────────────────────
# 2. CONFIRMED — sent when admin confirms
#    Transaction code is revealed here
# ─────────────────────────────────────────────
def email_confirmed(data: fullregistration, trip_name: str, transaction_code: str):
    html = f"""
    <!DOCTYPE html><html><head><style>
      body {{ font-family: 'Segoe UI', Arial, sans-serif; background:#f5f5f5; margin:0; padding:0; }}
      .wrap {{ max-width:600px; margin:40px auto; background:#fff; border-radius:12px; overflow:hidden; border:1px solid #e0e0e0; }}
      .header {{ background:#1a73e8; padding:32px; text-align:center; }}
      .header h1 {{ color:#fff; margin:0; font-size:24px; }}
      .header p {{ color:#cce0ff; margin:8px 0 0; font-size:14px; }}
      .body {{ padding:32px; color:#333; line-height:1.7; }}
      .code-box {{ background:#f0f7ff; border:1px dashed #1a73e8; padding:20px;
                   text-align:center; border-radius:10px; margin:24px 0; }}
      .code-box span {{ display:block; font-size:12px; color:#666; margin-bottom:6px; }}
      .code-box strong {{ font-size:22px; color:#1a73e8; letter-spacing:2px; }}
      .footer {{ background:#f1f3f4; padding:20px; text-align:center; font-size:12px; color:#888; }}
    </style></head><body>
    <div class="wrap">
      <div class="header">
        <h1>Booking Confirmed ✓</h1>
        <p>Your trip is officially booked!</p>
      </div>
      <div class="body">
        <p>Dear <strong>{data.fullname}</strong>,</p>
        <p>Great news! Your reservation for <strong>{trip_name}</strong> has been <strong>confirmed</strong> by our team. Please keep your transaction code safe — you will need it for any future inquiries.</p>
        <div class="code-box">
          <span>Your Transaction Code</span>
          <strong>{transaction_code}</strong>
        </div>
        <p>A member of our team will reach out shortly with the full itinerary and travel requirements.</p>
        <p>We look forward to hosting you!</p>
        <p>Best regards,<br><strong>The Travel Team</strong></p>
      </div>
      <div class="footer"><p>This is an automated message. Please do not reply directly to this email.</p></div>
    </div>
    </body></html>"""
    _send(data.email, f"Booking Confirmed — {trip_name}", html)


# ─────────────────────────────────────────────
# 3. CANCELLED — sent when reservation is deleted
# ─────────────────────────────────────────────
def email_cancelled(fullname: str, email: str, trip_name: str):
    html = f"""
    <!DOCTYPE html><html><head><style>
      body {{ font-family: 'Segoe UI', Arial, sans-serif; background:#f5f5f5; margin:0; padding:0; }}
      .wrap {{ max-width:600px; margin:40px auto; background:#fff; border-radius:12px; overflow:hidden; border:1px solid #e0e0e0; }}
      .header {{ background:#d32f2f; padding:32px; text-align:center; }}
      .header h1 {{ color:#fff; margin:0; font-size:24px; }}
      .header p {{ color:#ffcdd2; margin:8px 0 0; font-size:14px; }}
      .body {{ padding:32px; color:#333; line-height:1.7; }}
      .status-box {{ background:#fff3f3; border-left:4px solid #d32f2f;
                     padding:16px 20px; border-radius:8px; margin:24px 0; }}
      .status-box p {{ margin:0; font-size:15px; color:#7f0000; }}
      .footer {{ background:#f1f3f4; padding:20px; text-align:center; font-size:12px; color:#888; }}
    </style></head><body>
    <div class="wrap">
      <div class="header">
        <h1>Reservation Cancelled</h1>
        <p>We're sorry to see you go</p>
      </div>
      <div class="body">
        <p>Dear <strong>{fullname}</strong>,</p>
        <p>We wanted to let you know that your reservation for <strong>{trip_name}</strong> has been <strong>cancelled</strong>.</p>
        <div class="status-box">
          <p>✕ <strong>Status: Cancelled</strong> — Your spot has been released. If this was a mistake or you have questions, please contact us as soon as possible.</p>
        </div>
        <p>We hope to welcome you on a future trip.</p>
        <p>Best regards,<br><strong>The Travel Team</strong></p>
      </div>
      <div class="footer"><p>This is an automated message. Please do not reply directly to this email.</p></div>
    </div>
    </body></html>"""
    _send(email, f"Reservation Cancelled — {trip_name}", html)
