from smtplib import SMTP
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Environment, FileSystemLoader
import os

env = Environment(loader=FileSystemLoader('%s/../templates/' % os.path.dirname(__file__)))

def send_mail(context):
    template = env.get_template('./bookingmail.html')
    output = template.render()
    _send(output)    
    return "Mail sent successfully."

def _send(bodyContent):
    to_email = 'mattiaodorisio@live.it'
    from_email = 'mattia.noreply@gmail.com'
    subject = 'GoOutSafe booking!'
    message = MIMEMultipart()
    message['Subject'] = subject
    message['From'] = from_email
    message['To'] = to_email

    message.attach(MIMEText(bodyContent, "html"))
    msgBody = message.as_string()

    server = SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(from_email, '+++')
    server.sendmail(from_email, to_email, msgBody)

    server.quit()