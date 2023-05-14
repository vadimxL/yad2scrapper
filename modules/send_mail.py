import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import yaml

logger = logging.getLogger('webScrapper')


def send_email(attachment_file_paths, start_page, end_page, start_time, end_time):
    # Open the YAML file
    with open('db/email.yml', 'r') as file:
        # Load the YAML data
        data = yaml.safe_load(file)

    # Set up the email
    # Set up the SMTP server credentials
    smtp_host = data['smtp_host']  # 'smtp.gmail.com'
    smtp_port = data['smtp_port']  # 587
    smtp_username = data['smtp_username']  # 'malinvadim88@gmail.com'
    smtp_password = data['smtp_password']  # 'iqraxjplttxucyag'

    # Set up the email content
    sender = data['sender']  # 'malinvadim88@gmail.com'
    recipient = data['recipient']  # 'vadimski30@gmail.com'
    subject = 'Email Subject'
    body = 'Data Scrapping Report'
    message = "Message: {}\nPages Range:{} - {}\nJob Start Time: {}\nJob Finished Time: {}".format(body, start_page,
                                                                                                   end_page, start_time,
                                                                                                   end_time)

    # Create a multipart message and set headers
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = recipient
    msg['Subject'] = subject

    # Add the message body to the email
    msg.attach(MIMEText(message, 'plain'))

    for file_path in attachment_file_paths:
        with open(file_path, 'rb') as file:
            part = MIMEApplication(file.read())
            part.add_header('Content-Disposition', 'attachment', filename=file_path)
            msg.attach(part)

    # Create an SMTP session
    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls()  # Enable encryption for security
        server.login(smtp_username, smtp_password)
        server.send_message(msg)

    print('Email sent successfully!')
    logger.info("[>]. Report '{}' has been successfully emailed\n".format(attachment_file_paths))
