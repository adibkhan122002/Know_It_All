import sqlite3
import smtplib
import os
from email.mime.text import MIMEText

def notification():
    # Load config from environment variables
    DB_PATH = os.environ.get("DB_PATH", "library.db")

    SMTP_SERVER = os.environ["SMTP_SERVER"]
    SMTP_PORT = int(os.environ.get("SMTP_PORT", 587))
    SMTP_USERNAME = os.environ["SMTP_USERNAME"]
    SMTP_PASSWORD = os.environ["SMTP_PASSWORD"]

    EMAIL_FROM = os.environ["EMAIL_FROM"]

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT members.email, borrows.return_date
        FROM members
        INNER JOIN borrows ON members.member_name = borrows.bmember_id
        WHERE borrows.return_date = DATE('now', '+2 days')
    """)

    results = cursor.fetchall()

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)

        for email, return_date in results:
            message = MIMEText(
                f"Please remember to return your library book by {return_date}."
            )
            message["Subject"] = "Library Book Return Reminder"
            message["From"] = EMAIL_FROM
            message["To"] = email

            server.sendmail(EMAIL_FROM, email, message.as_string())

    conn.close()

notification()
