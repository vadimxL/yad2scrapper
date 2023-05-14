from .emailUtils import *
import yaml
import logging


logger = logging.getLogger('webScrapper')

emailConf = './db/email.yml'
emailData = None

with open(emailConf, 'r') as f:
    emailData = yaml.load(f, Loader=yaml.FullLoader)

if not emailData:
    print("Email configuration seems corrupted")
    exit(1)

username = emailData.get('username')
password = emailData.get('password')
# smtpPort = emailData.get('smtpPort')
smtpServer = emailData.get('smtpServer')
receiver = emailData.get('receiver')
subject = emailData.get('subject')
body = emailData.get('body')

ccContact = emailData.get('ccContact')


def sendEmail(attachment,sPage, ePage, startTime, endTime):
    attachments = []
    attachments.append(attachment)
    emailConn = None
    email = None
    message = "Message: {}\nPages Range:{} - {}\nJob Start Time: {}\nJob Finished Time: {}".format(body, sPage, ePage, startTime, endTime)

    try:
        email = Email(to=receiver, from_=username, subject=subject, cc=ccContact, message=message, attachments=attachments)
        emailConn = EmailConnection(username=username, password=password, server=smtpServer)
        response = emailConn.send(email, from_=username, to=receiver)

        logger.info("[>]. Report '{}' has been successfully emailed\n".format(attachment))
        
    except Exception as e:
        logger.error("[ERROR]. Unable to send email for following reasons:")
        raise e
