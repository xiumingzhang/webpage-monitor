from email.mime.text import MIMEText
import smtplib


def read_file(path):
    with open(path, 'rb') as file_handle:
        content = file_handle.read()
    return content.decode()


def write_file(str_, path):
    with open(path, 'wb') as file_handle:
        file_handle.write(str_.encode())


def folder_name_from_url(url):
    folder_name = url.rstrip('/')
    folder_name = folder_name.replace('http://', '').replace('https://', '')
    folder_name = folder_name.replace('/', '_')
    folder_name = folder_name.replace('?', '_')
    folder_name = folder_name.replace('&', '_')
    folder_name = folder_name.replace(':', '_')
    return folder_name


def email_oneself(msg,
                  gmail,
                  subject='Untitled',
                  pswd_path='./gmail_app_pswd'):
    pswd = read_file(pswd_path)
    pswd = pswd.strip()

    to_emails = [gmail]
    from_email = gmail

    msg = MIMEText(msg)
    msg['Subject'] = subject
    msg['To'] = ', '.join(to_emails)
    msg['From'] = from_email

    mail = smtplib.SMTP('smtp.gmail.com', 587)
    mail.starttls()
    mail.login(gmail, pswd)
    mail.sendmail(from_email, to_emails, msg.as_string())
    mail.quit()
