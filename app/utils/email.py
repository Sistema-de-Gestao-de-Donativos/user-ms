from auth.env import get_control_panel_env, get_email_env


control_panel_env = get_control_panel_env()
CONTROL_PANEL_URL = control_panel_env.get("URL")
FORGOT_PASSWORD_URL = CONTROL_PANEL_URL + \
    control_panel_env.get("Reset Password Endpoint")


def connect_to_email_server():
    import smtplib
    """
    Function to connect to the e-mail server.

    Returns:
        smtplib.SMTP: The e-mail server.
    """

    email_env = get_email_env()
    EMAIL_SERVER, EMAIL_PORT, EMAIL_ADDRESS, EMAIL_SECRET = \
        email_env.get("Server"), email_env.get("Port"), \
        email_env.get("Address"), email_env.get("Secret")

    try:
        server = smtplib.SMTP(EMAIL_SERVER, EMAIL_PORT)
        server.starttls()
        response = server.login(EMAIL_ADDRESS, EMAIL_SECRET)
        WELCOME_SUCCESS_CODE = 235
        if response[0] != WELCOME_SUCCESS_CODE:
            print("Something weird happened on the e-mail server.", response)
            return False

        return server

    except Exception as e:
        print("Error connecting to the e-mail server.", e)
        return False


def emails_to_str_list(emails: list[str] | str):
    """
    Function to convert a list of e-mails to a list of strings.

    Args:
        emails (list[str] | str): The e-mails to convert.

    Returns:
        str: The converted e-mails as a string separated by commas.
    """

    if isinstance(emails, str):
        emails = [emails]
    emails = ",".join(emails)
    return emails


def send_custom_email(email_addresses: list[str] | str, subject: str, body: str):
    from email.message import EmailMessage
    """
    Function to send e-mails.

    Args:
        email_addresses (list[str] | str): The e-mail addresses to send the e-mail to.
        subject (str): The subject of the e-mail.
        body (str): The body of the e-mail.

    Raises:
        Exception: If something weird happens on the e-mail server.
    """

    mail = EmailMessage()
    mail.set_content(body)
    mail["Subject"] = subject
    mail["To"] = emails_to_str_list(email_addresses)

    server = connect_to_email_server()
    if not server:
        return False

    server.send_message(mail)
    server.quit()

    return True


def send_welcome_html_email(
    email_address: list[str] | str,
    subject: str = "Mithra Controller Invitation",
    body: str = f"Welcome to the Mithra Controller v0.1\nYou have been invited to join the Beta version of the Mithra Controller!\nPlease click the link below to finish creating your account",
    reset_password_token: str = None,
):
    from email.message import EmailMessage
    from email.utils import make_msgid
    """
    Function to send a welcome e-mail.

    Args:
        email_address (list[str] | str): The e-mail address to send the e-mail to.
        subject (str, optional): The subject of the e-mail. Defaults to "Mithra Controller Invitation".
        body (str, optional): The body of the e-mail.
        reset_password_token (str, optional): The token to reset the password.

    Returns:
        bool: Whether the e-mail was sent successfully.
    """

    mail = EmailMessage()
    mail["Subject"] = subject
    mail["To"] = emails_to_str_list(email_address)
    fallback_content = body
    mail.set_content(fallback_content)

    html_template = open("static/welcome_email_template.html", "r").read()

    html_template = html_template.replace("{{subject}}", subject)

    html_template = html_template.replace("{{body}}", body)

    CP_CREATE_ACCOUNT_ENDPOINT = control_panel_env.get(
        "Reset Password Endpoint")
    EMAIL_INVITE_CREATE_ACCOUNT_URL = CONTROL_PANEL_URL + CP_CREATE_ACCOUNT_ENDPOINT

    reset_password_origin = "emailInvite"
    reset_password_link = f"{EMAIL_INVITE_CREATE_ACCOUNT_URL}?t={reset_password_token}&origin={reset_password_origin}"
    html_template = html_template.replace(
        "{{create_account_link}}", reset_password_link)

    welcome_logo_cid = make_msgid()
    html_template = html_template.replace(
        "{{welcome_logo_cid}}", welcome_logo_cid[1:-1])

    mail.add_alternative(html_template, subtype="html")

    with open("static/logo.png", "rb") as img:
        mail.get_payload()[1].add_related(
            img.read(), "image", "png", cid=welcome_logo_cid)

    server = connect_to_email_server()
    if not server:
        return False

    server.send_message(mail)
    server.quit()

    return True
