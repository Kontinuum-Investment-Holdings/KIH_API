import traceback
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import time
from typing import List

import logger
import communication.email.constants as constants


def send_email(to_address_list: List[str], email_subject: str, email_content: str) -> None:
    #   Getting email object
    email = MIMEMultipart()
    email["Subject"] = email_subject
    email["From"] = constants.email_account
    email.attach(MIMEText(email_content, 'html'))

    #   Connecting to the SMTP server
    start_time = time.time()
    smtp_server = smtplib.SMTP("smtp.office365.com", port=587)
    smtp_server.starttls()
    logger.performance(constants.execution_type__Email_Server, "Connection Establishment", "", start_time)

    #   Authenticating
    start_time = time.time()

    try:
        smtp_server.login("kavindu@outlook.com", "K@v1n|)()#Micr.1")
    except Exception:
        traceback.print_exc()

    logger.performance(constants.execution_type__Email_Server, "Authentication", "", start_time)

    #   Sending email
    logger.info("Sending email to " + str(len(to_address_list)) + " recipients")

    email = MIMEMultipart()
    email["Subject"] = email_subject
    email["From"] = constants.email_account
    email["To"] = constants.email_account
    email.attach(MIMEText(email_content, 'html'))

    start_time = time.time()
    smtp_server.send_message(from_addr=constants.email_account, to_addrs=to_address_list, msg=email)
    logger.performance(constants.execution_type__Email_Server, "Sending Email", str(email), start_time)

    #   Disconnecting from the SMTP server
    smtp_server.quit()