from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
import credentials as cr
import config.config as c

#Sends an email
def sendMail(subject, text):
    gmailUser, gmailPassword = cr.getcreds(c.GMAILCREDS)
    recipientfile = open(c.MAILRECIPIENTLISTDIR,"r")
    recipients = recipientfile.readlines(); 
    try:
        msg = MIMEMultipart()
	msg['From'] = gmailUser
	msg['Subject'] = subject
	msg.attach(MIMEText(text))
	mailServer = smtplib.SMTP('smtp.gmail.com', 587)
	mailServer.ehlo()
	mailServer.starttls()
	mailServer.ehlo()
	mailServer.login(gmailUser, gmailPassword)
	msg['To'] = "alarmslist"
	mailServer.sendmail(gmailUser, recipients, msg.as_string())
	mailServer.close()
    except:
        pass
    return 

