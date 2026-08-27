import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dotenv import load_dotenv


load_dotenv()


SMTP_HOST = os.getenv(
    "SMTP_HOST",
    ""
)

SMTP_PORT = int(
    os.getenv(
        "SMTP_PORT",
        "587"
    )
)

SMTP_USERNAME = os.getenv(
    "SMTP_USERNAME",
    ""
)

SMTP_PASSWORD = os.getenv(
    "SMTP_PASSWORD",
    ""
)

EMAIL_FROM = os.getenv(
    "EMAIL_FROM",
    SMTP_USERNAME
)


def send_email(
    to_email: str,
    subject: str,
    message: str
):
    if not all(
        [
            SMTP_HOST,
            SMTP_USERNAME,
            SMTP_PASSWORD,
            EMAIL_FROM
        ]
    ):
        print(
            "Email configuration is missing. "
            "Email was not sent."
        )

        return False

    try:
        email = MIMEMultipart()

        email["From"] = EMAIL_FROM
        email["To"] = to_email
        email["Subject"] = subject

        email.attach(
            MIMEText(
                message,
                "plain"
            )
        )

        with smtplib.SMTP(
            SMTP_HOST,
            SMTP_PORT
        ) as server:

            server.starttls()

            server.login(
                SMTP_USERNAME,
                SMTP_PASSWORD
            )

            server.sendmail(
                EMAIL_FROM,
                to_email,
                email.as_string()
            )

        return True

    except Exception as exc:
        print(
            f"Failed to send email: {str(exc)}"
        )

        return False