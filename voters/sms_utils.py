import re
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

def format_phone_number_e164(phone_number: str) -> str:
    """
    Formats a Sri Lankan or international phone number to E.164 format (+94XXXXXXXXX).
    e.g.:
      0771234567 -> +94771234567
      771234567  -> +94771234567
      +94771234567 -> +94771234567
      94771234567  -> +94771234567
    """
    clean_number = re.sub(r'[\s\-\(\)]', '', phone_number.strip())
    if clean_number.startswith('+'):
        return clean_number
    if clean_number.startswith('0'):
        return f"+94{clean_number[1:]}"
    if clean_number.startswith('94'):
        return f"+{clean_number}"
    # Default assumption for 9-digit mobile
    if len(clean_number) == 9:
        return f"+94{clean_number}"
    return f"+{clean_number}"


def send_verification_sms(to_mobile: str, code: str) -> tuple[bool, str]:
    """
    Sends a 6-digit verification code to the user's mobile number via Twilio.
    Returns (success: bool, message: str)
    """
    account_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', None)
    auth_token = getattr(settings, 'TWILIO_AUTH_TOKEN', None)
    from_number = getattr(settings, 'TWILIO_PHONE_NUMBER', None)

    if not account_sid or not auth_token or not from_number:
        err_msg = "Twilio credentials are not configured in settings."
        logger.error(err_msg)
        return False, err_msg

    try:
        from twilio.rest import Client
        formatted_to = format_phone_number_e164(to_mobile)
        client = Client(account_sid, auth_token)

        message_body = (
            f"Your Election Management System (EMS) verification code is: {code}. "
            f"This code will expire in 5 minutes."
        )

        message = client.messages.create(
            body=message_body,
            from_=from_number,
            to=formatted_to
        )

        logger.info(f"Twilio SMS sent to {formatted_to}. SID: {message.sid}")
        print(f"[Twilio] SMS successfully dispatched to {formatted_to} (SID: {message.sid})")
        return True, message.sid

    except Exception as e:
        logger.exception(f"Failed to send Twilio SMS to {to_mobile}: {e}")
        print(f"[Twilio Error] Failed to send SMS to {to_mobile}: {e}")
        return False, str(e)
