from smtplib import SMTP
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Environment, FileSystemLoader
from monolith.database import Notification, User, db
from monolith.background import celery
from datetime import datetime
import os

env = Environment(loader=FileSystemLoader('%s/../templates/' % os.path.dirname(__file__)))

@celery.task
def send_contact_notification():
    """
        Send the email notification to users at risk
    """
    print("Mail sending")
    notifications = Notification.query.filter_by(email_sent=False).filter_by(user_notification=True)
    count = 0
    for notification in notifications:
        user = notification.user
        if user != None and user.email != None:
            notification.email_sent = True
            db.session.commit()
            template = env.get_template('./mail_notification.html')
            output = template.render(dest=user, date=notification.date.strftime('%Y-%m-%d at %H:%M'))
            _send(notification, output)
            print("email field updated")
            count += 1

    print(f'{count} email(s) sent')

@celery.task
def _send(notification, bodyContent):

    to_email = notification.user.email
    from_email = 'GoOutSafe.ase@gmail.com'
    subject = 'GoOutSafe contact notification'
    message = MIMEMultipart()
    message['Subject'] = subject
    message['From'] = from_email
    message['To'] = to_email

    message.attach(MIMEText(bodyContent, "html"))
    msgBody = message.as_string()

    print(f'Sending email to {to_email}')
    server = SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(from_email, 'AseSquad5')
    server.sendmail(from_email, to_email, msgBody)

    server.quit()
