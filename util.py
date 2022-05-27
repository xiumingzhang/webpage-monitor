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


def email_myself(msg,
                 subject='Untitled',
                 email='xiuming6zhang@gmail.com',
                 pswd_path='./gmail_app_pswd'):
    pswd = read_file(pswd_path)
    pswd = pswd.strip()

    to_emails = [email]
    from_email = email

    msg = MIMEText(msg)
    msg['Subject'] = subject
    msg['To'] = ', '.join(to_emails)
    msg['From'] = from_email

    mail = smtplib.SMTP('smtp.gmail.com', 587)
    mail.starttls()
    mail.login(email, pswd)
    mail.sendmail(from_email, to_emails, msg.as_string())
    mail.quit()


def format_print(msg, fmt):
    '''Prints a message with format.
    Args:
        msg (str): Message to print.
        fmt (str): Format; try your luck with any value -- don't worry; if
            it's illegal, you will be prompted with all legal values.
    Raises:
        ValueError: If the input format is illegal.
    '''
    fmt_strs = {
        'header': '\033[95m',
        'warn': '\033[93m',
        'fail': '\033[91m',
        'bold': '\033[1m',
        'underline': '\033[4m'
    }

    if fmt in fmt_strs.keys():
        start_str = fmt_strs[fmt]
        end_str = '\033[0m'

    elif len(fmt) == 1:
        start_str = '\n<' + ''.join([fmt] * 78) + '\n\n'  # as per PEP8
        end_str = '\n' + start_str[2:-2] + '>\n'

    else:
        raise ValueError(
            ('Legal values for fmt: %s, plus any single character '
             '(which will be repeated into the line separator), '
             'but input is %s') % (list(fmt_strs.keys()), fmt))

    print(start_str + msg + end_str)
