import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

username=os.environ["username"]
password=os.environ["password"]

def send_mail(html=None,text='',subject='Signup to join pokerplanner',from_email=username,to_emails=[]):
    msg=MIMEMultipart('alternative')
    msg['From']=from_email
    msg['To']=", ".join(to_emails)
    msg['Subject']=subject

    html="""
    <!DOCTYPE html>
    <html lang="en">
        <body>
            <p>Hello,</p>
            <p>You haven't signed up yet click here to join pokerplanner and start estimating tickets.</p>
            <a href="http://127.0.0.1:5500/index.html#!/">Click here to signup.</a>
        </body>
    </html>
    """
    
    html_part = MIMEText(html, 'html')
    msg.attach(html_part)
    msg_str=msg.as_string()


    server=smtplib.SMTP(host='smtp.gmail.com',port=587)
    server.ehlo()
    server.starttls()
    server.login(username,password)
    server.sendmail(from_email,to_emails,msg_str)
    server.quit()

