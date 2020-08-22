from subprocess import Popen, PIPE
from email.mime.text import MIMEText
import smtplib


def call(cmd, cwd=None, silence_stdout=False):
    process = Popen(cmd, stdout=PIPE, stderr=PIPE, cwd=cwd, shell=True)

    stdout, stderr = process.communicate() # waits for completion
    stdout, stderr = stdout.decode(), stderr.decode()

    if not silence_stdout:
        if stdout != '':
            format_print(stdout, 'okblue')

    if stderr != '':
        format_print(cmd, 'header')
        format_print(stderr, 'fail')


def email_myself(
        msg, subject="Untitled", email='xiuming6zhang@gmail.com',
        pswd_path='./gmail_app_pswd'):
    with open(pswd_path, 'r') as h:
        pswd = h.readlines()
    pswd = pswd[0].strip()

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
    """Prints a message with format.
    Args:
        msg (str): Message to print.
        fmt (str): Format; try your luck with any value -- don't worry; if
            it's illegal, you will be prompted with all legal values.
    Raises:
        ValueError: If the input format is illegal.
    """
    fmt_strs = {
        'header': '\033[95m',
        'warn': '\033[93m',
        'fail': '\033[91m',
        'bold': '\033[1m',
        'underline': '\033[4m'}
    if fmt in fmt_strs.keys():
        start_str = fmt_strs[fmt]
        end_str = '\033[0m'
    elif len(fmt) == 1:
        start_str = "\n<" + "".join([fmt] * 78) + '\n\n' # as per PEP8
        end_str = '\n' + start_str[2:-2] + ">\n"
    else:
        raise ValueError(
            ("Legal values for fmt: %s, plus any single character "
             "(which will be repeated into the line separator), "
             "but input is '%s'") % (list(fmt_strs.keys()), fmt))
    print(start_str + msg + end_str)
