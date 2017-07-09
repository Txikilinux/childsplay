#! /usr/bin/python

#create logger, logger was configured in SPLoggin
import logging
module_logger = logging.getLogger("schoolsplay.Mail")

import smtplib
from time import strftime
from email.MIMEMultipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.MIMEText import MIMEText
from email import Encoders

import os

class SendmailError(Exception):
    pass

#Email versturen 
def mail(text='No description given', imgpath=''):
    #Email van degene die de mail verstuurd
    gmail_user = "splogfiles@gmail.com"# pass is spam2010
    #Email van de mensen naar wie je een mail wilt sturen
    #gmail_to = ["hjvankatwijk@gmail.com", "acidjunk@gmail.com", "stas.zytkiewicz@gmail.com"]
    gmail_to = ["splogfiles@gmail.com"]# pass is spam2010
    #Wachtwoord van degene die de mail verstuurd
    gmail_pwd = "spam2010"
    
    logpath = os.path.expanduser(os.path.join('~', '.schoolsplay.rc', 'schoolsplay.log'))

    subject = "schoolsplaylogfile: " + str(strftime("%d-%m-%Y %H:%M:%S"))
    module_logger.debug("Starting to mail logfile")
    for i in range(len(gmail_to)):  
        msg = MIMEMultipart()
        msg["From"] = gmail_user
        msg["To"] = gmail_to[i]
        msg["Subject"] = subject
        msg.attach(MIMEText(text))

        txt = MIMEText(open(logpath,'r').read())
        txt.add_header('Content-Disposition', 'attachment', filename=logpath)
        msg.attach(txt)

        if imgpath:
            img = MIMEImage(open(imgpath,'rb').read())
            img.add_header('Content-Disposition', 'attachment', filename=imgpath)
            msg.attach(img)
        try:
            mailServer = smtplib.SMTP("smtp.gmail.com", 587, timeout=5)
            mailServer.ehlo()
            mailServer.starttls()
            mailServer.ehlo()
            mailServer.login(gmail_user, gmail_pwd)
            mailServer.sendmail(gmail_user, gmail_to[i], msg.as_string())
        except Exception, msg:
            module_logger.debug("Failed to send mail, please report this.%s" % msg)
            raise SendmailError,msg
        else:
            mailServer.close()
            module_logger.debug("Mail send to: %s" % str(gmail_to[i]))
        finally:
            mailServer.close()

if __name__ == '__main__':
    # Beware that this will create a new logfile so the file mailed will be this logfile
    import SPLogging
    SPLogging.set_level('debug')
    SPLogging.start()

    img = '/home/stas/.schoolsplay.rc/test.jpeg'
    

    mail(ticketnum='0',imgpath=img)
