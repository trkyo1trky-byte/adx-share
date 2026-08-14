import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from ..core.config import settings
import logging

logger = logging.getLogger(__name__)

def send_email(to_email: str, subject: str, body: str, html: bool = False) -> bool:
    """إرسال بريد إلكتروني عبر SMTP"""
    try:
        if html:
            msg = MIMEMultipart()
            msg.attach(MIMEText(body, 'html', 'utf-8'))
        else:
            msg = MIMEText(body, 'plain', 'utf-8')
            
        msg['Subject'] = subject
        msg['From'] = settings.SMTP_FROM
        msg['To'] = to_email

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            if settings.SMTP_USER and settings.SMTP_PASSWORD:
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)
        logger.info(f"Email sent to {to_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return False

def send_verification_email(to_email: str, token: str) -> bool:
    """إرسال بريد تأكيد البريد الإلكتروني"""
    link = f"{settings.FRONTEND_URL}/verify-email?token={token}"
    subject = "تأكيد البريد الإلكتروني - ADX SHARES"
    body = f"""
    <h2>مرحباً بك في ADX SHARES</h2>
    <p>يرجى النقر على الرابط التالي لتأكيد بريدك الإلكتروني:</p>
    <a href="{link}">{link}</a>
    <p>إذا لم تقم بإنشاء حساب، يرجى تجاهل هذه الرسالة.</p>
    """
    return send_email(to_email, subject, body, html=True)

def send_reset_email(to_email: str, token: str) -> bool:
    """إرسال بريد إعادة تعيين كلمة المرور"""
    link = f"{settings.FRONTEND_URL}/reset-password?token={token}"
    subject = "إعادة تعيين كلمة المرور - ADX SHARES"
    body = f"""
    <h2>إعادة تعيين كلمة المرور</h2>
    <p>انقر على الرابط التالي لإعادة تعيين كلمة المرور:</p>
    <a href="{link}">{link}</a>
    <p>إذا لم تطلب إعادة التعيين، يرجى تجاهل هذه الرسالة.</p>
    <p>الرابط صالح لمدة ساعة واحدة.</p>
    """
    return send_email(to_email, subject, body, html=True)