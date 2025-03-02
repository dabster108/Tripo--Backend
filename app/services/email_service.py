import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from ..core.config import settings
from ..core.logging import logger

def send_verification_email(to_email: str, verification_code: str):
    """
    Send verification email with code
    """
    # For now just log the verification code
    logger.info(f"VERIFICATION CODE for {to_email}: {verification_code}")
    
    # In production, implement actual email sending:
    if not settings.SMTP_SERVER:
        logger.warning("SMTP server not configured. Email not sent.")
        return False
    
    try:
        msg = MIMEMultipart()
        msg['From'] = settings.EMAIL_FROM
        msg['To'] = to_email
        msg['Subject'] = "Verify your Lanceraa account"
        
        body = f"""
        <html>
          <body>
            <h2>Welcome to Lanceraa!</h2>
            <p>Your verification code is: <strong>{verification_code}</strong></p>
            <p>This code will expire in 30 minutes.</p>
          </body>
        </html>
        """
        
        msg.attach(MIMEText(body, 'html'))
        
        server = smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT)
        server.starttls()
        server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        logger.info(f"Verification email sent to {to_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        return False