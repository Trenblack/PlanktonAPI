import resend
from typing import Dict, List, Union
from app.settings import (
    RESEND_API_KEY,
    EMAIL_SENDER_DOMAIN,
    EMAIL_SENDER_NAME,
    TWO_FACTOR_CODE_EXPIRE_MINUTES,
    EMAIL_VERIFICATION_EXPIRE_MINUTES,
    PASSWORD_RESET_EXPIRE_MINUTES
)

resend.api_key = RESEND_API_KEY

def send_2fa_email(
    to: Union[str, List[str]],
    code: str,
    name: str = EMAIL_SENDER_NAME,
    domain: str = EMAIL_SENDER_DOMAIN,
    subject: str = "Your Authentication Code",
    expire_time_minutes: int = TWO_FACTOR_CODE_EXPIRE_MINUTES
) -> Dict:
    """
    Send a 2FA verification email with a code.
    
    Args:
        to: Email address(es) of the recipient(s)
        code: The verification code to be sent
        name: Company or service name
        domain: Email domain (for the sender address)
        subject: Email subject line
        expire_time_minutes: How long the code remains valid in minutes
    
    Returns:
        Dict: The response from the email service
    """
    # Convert single email to list format
    if isinstance(to, str):
        to = [to]
    
    params: resend.Emails.SendParams = {
        "from": f"{name} <no-reply@{domain}>",
        "to": to,
        "subject": f"{name} - {subject}",
        "html": f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Two-Factor Authentication Code</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ text-align: center; padding: 20px 0; }}
                .logo {{ font-size: 24px; font-weight: bold; color: #4a154b; }}
                .content {{ background-color: #f9f9f9; padding: 30px; border-radius: 5px; color: #333333; }}
                .code {{ font-size: 32px; font-weight: bold; text-align: center; padding: 15px; 
                        background-color: #eee; margin: 20px 0; letter-spacing: 5px; }}
                .security-tip {{ font-size: 13px; color: #666; margin: 20px 0; font-style: italic; border-top: 1px solid #e0e0e0; border-bottom: 1px solid #e0e0e0; padding: 12px 0; }}
                .footer {{ text-align: center; font-size: 12px; color: #999999; margin-top: 30px; }}
                .button {{ 
                    display: inline-block; 
                    background-color: #4a154b !important; 
                    color: #ffffff !important; 
                    padding: 12px 24px; 
                    text-decoration: none; 
                    border-radius: 4px; 
                    font-weight: bold; 
                    margin: 15px 0;
                }}
                a.button {{ color: #ffffff !important; }}
                p {{ color: #333333; }}
                .content a:not(.button) {{ color: #333333; text-decoration: underline; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">{name}</div>
                </div>
                <div class="content">
                    <p>Hello,</p>
                    <p>Please use the following verification code to complete your login:</p>
                    <div class="code">{code}</div>
                    <p>This code will expire in {expire_time_minutes} minutes.</p>
                    <p class="security-tip">If you didn't request this code, we recommend updating your password immediately.</p>
                    <p>Best regards,<br>The {name} Team</p>
                </div>
                <div class="footer">
                    <p>© {2025} {name}. All rights reserved.</p>
                    <p>This is an automated message, please do not reply to this email.</p>
                </div>
            </div>
        </body>
        </html>
        """,
    }
    email: resend.Email = resend.Emails.send(params)
    return email

def send_password_reset_email(
    to: Union[str, List[str]],
    reset_link: str,
    name: str = EMAIL_SENDER_NAME,
    domain: str = EMAIL_SENDER_DOMAIN,
    subject: str = "Password Reset Request",
    expire_time_minutes: int = PASSWORD_RESET_EXPIRE_MINUTES
) -> Dict:
    """
    Send a password reset email with a secure link.
    
    Args:
        to: Email address(es) of the recipient(s)
        reset_link: The password reset link
        name: Company or service name
        domain: Email domain (for the sender address)
        subject: Email subject line
        expire_time_minutes: How long the link remains valid in minutes
    
    Returns:
        Dict: The response from the email service
    """
    # Convert single email to list format
    if isinstance(to, str):
        to = [to]
    
    params: resend.Emails.SendParams = {
        "from": f"{name} <no-reply@{domain}>",
        "to": to,
        "subject": f"{name} - {subject}",
        "html": f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Password Reset</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ text-align: center; padding: 20px 0; }}
                .logo {{ font-size: 24px; font-weight: bold; color: #4a154b; }}
                .content {{ background-color: #f9f9f9; padding: 30px; border-radius: 5px; }}
                .security-tip {{ font-size: 13px; color: #666; margin: 20px 0; font-style: italic; border-top: 1px solid #e0e0e0; border-bottom: 1px solid #e0e0e0; padding: 12px 0; }}
                .footer {{ text-align: center; font-size: 12px; color: #999; margin-top: 30px; }}
                .button {{ 
                    display: inline-block; 
                    background-color: #4a154b !important; 
                    color: #ffffff !important; 
                    padding: 12px 24px; 
                    text-decoration: none; 
                    border-radius: 4px; 
                    font-weight: bold; 
                    margin: 15px 0;
                    text-align: center;
                }}
                a.button {{ color: #ffffff !important; }}
                .button-container {{ text-align: center; margin: 25px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">{name}</div>
                </div>
                <div class="content">
                    <p>Hello,</p>
                    <p>We received a request to reset your password. Please click the button below to create a new password:</p>
                    <div class="button-container">
                        <a href="{reset_link}" class="button" style="color: #ffffff !important; background-color: #4a154b !important; text-decoration: none;">Reset Password</a>
                    </div>
                    <p>This link will expire in {expire_time_minutes} minutes.</p>
                    <p>If the button doesn't work, copy and paste the following link into your browser:</p>
                    <p style="word-break: break-all; font-size: 12px;">{reset_link}</p>
                    <p>Best regards,<br>The {name} Team</p>
                </div>
                <div class="footer">
                    <p>© {2025} {name}. All rights reserved.</p>
                    <p>This is an automated message, please do not reply to this email.</p>
                </div>
            </div>
        </body>
        </html>
        """,
    }
    email: resend.Email = resend.Emails.send(params)
    return email

def send_account_verification_email(
    to: Union[str, List[str]],
    verification_link: str,
    name: str = EMAIL_SENDER_NAME,
    domain: str = EMAIL_SENDER_DOMAIN,
    subject: str = "Verify Your Account",
    expire_time_minutes: int = EMAIL_VERIFICATION_EXPIRE_MINUTES
) -> Dict:
    """
    Send an account verification email with an activation link.
    
    Args:
        to: Email address(es) of the recipient(s)
        verification_link: The account verification link
        name: Company or service name
        domain: Email domain (for the sender address)
        subject: Email subject line
        expire_time_minutes: How long the link remains valid in minutes
    
    Returns:
        Dict: The response from the email service
    """
    # Convert single email to list format
    if isinstance(to, str):
        to = [to]
    
    params: resend.Emails.SendParams = {
        "from": f"{name} <no-reply@{domain}>",
        "to": to,
        "subject": f"{name} - {subject}",
        "html": f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Verify Your Account</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ text-align: center; padding: 20px 0; }}
                .logo {{ font-size: 24px; font-weight: bold; color: #4a154b; }}
                .content {{ background-color: #f9f9f9; padding: 30px; border-radius: 5px; }}
                .footer {{ text-align: center; font-size: 12px; color: #999; margin-top: 30px; }}
                .button {{ 
                    display: inline-block; 
                    background-color: #4a154b !important; 
                    color: #ffffff !important; 
                    padding: 12px 24px; 
                    text-decoration: none; 
                    border-radius: 4px; 
                    font-weight: bold; 
                    margin: 15px 0;
                    text-align: center;
                }}
                a.button {{ color: #ffffff !important; }}
                .button-container {{ text-align: center; margin: 25px 0; }}
                .welcome {{ font-size: 18px; font-weight: bold; margin-bottom: 15px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">{name}</div>
                </div>
                <div class="content">
                    <p class="welcome">Welcome to {name}!</p>
                    <p>Thank you for signing up. Please verify your email address to activate your account:</p>
                    <div class="button-container">
                        <a href="{verification_link}" class="button" style="color: #ffffff !important; background-color: #4a154b !important; text-decoration: none;">Verify My Account</a>
                    </div>
                    <p>This link will expire in {expire_time_minutes} minutes.</p>
                    <p>If the button doesn't work, copy and paste the following link into your browser:</p>
                    <p style="word-break: break-all; font-size: 12px;">{verification_link}</p>
                    <p>We're excited to have you on board!</p>
                    <p>Best regards,<br>The {name} Team</p>
                </div>
                <div class="footer">
                    <p>© {2025} {name}. All rights reserved.</p>
                    <p>This is an automated message, please do not reply to this email.</p>
                </div>
            </div>
        </body>
        </html>
        """,
    }
    email: resend.Email = resend.Emails.send(params)
    return email
