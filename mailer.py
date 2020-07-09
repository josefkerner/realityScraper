try:

    import smtplib
    import mimetypes
    from email.mime.multipart import MIMEMultipart
    from email import encoders
    from email.message import Message
    from email.mime.text import MIMEText
except ImportError as e:
    print("Failed to import required classes")
    exit(1)


mails =  ['vostram@psp.cz','press@kscm.cz','leftnews@kscm.cz','info@kscm.cz']


def sendMail(text, html=None, subject=None, recipient=None, sender=None):
    if subject is None:
        subject = 'Notification from Cloudera Analytical Platform Request Management system'
    if sender is None:
        sender = "cloudera-ap@skoda-auto.cz"

    if html is not None:
        msg = MIMEMultipart('alternative')
        msg.attach(MIMEText(html, 'html', 'utf-8'))
    else:
        msg = MIMEMultipart()  # create a message

    # setup the parameters of the message
    msg['From'] = sender
    msg['To'] = recipient
    msg['Subject'] = subject

    # add in the message body
    msg.attach(MIMEText(text, 'plain'))

    # self.utils.log(subject)
    # self.utils.log("From : " + sender)
    # self.utils.log("To : " + recipient)
    # self.utils.log(text)

    try:
        if self.client == None:
            raise ConnectionError("Failed to connect to Skoda email server")
        self.client.send_message(msg)
        self.utils.log("Successfully sent email")
    except Exception as e:
        self.utils.log("Error: unable to send email because of error : " + str(e))

    for mail in mails:
        text = "Zavražděna komunisty"
        html = None
        sender = "milada@horakova.cz"
        recipient = mail
        subject = "Byla jsem zavražděna komunisty"

        sendMail(text=text,
                 html=html,
                 subject=subject,
                 recipient=recipient,
                 sender=sender
                 )