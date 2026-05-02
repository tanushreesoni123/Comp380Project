"""
a) Module/Class Name: EmailService 
b) Date: May 1, 2026
c) Programmer: Tanushree Soni 

d) Description:
   - handles sending booking confirmation emails to customers.
   - uses SMTP (Simple Mail Transfer Protocol) to send emails with booking details
   such as movie name, theatre, show time, seats, and total amount.
   - supports both booking confirmation and payment confirmation scenarios.
   """

import smtplib
from email.message import EmailMessage


class EmailService:
    def __init__(
        self,
        smtp_server: str,
        smtp_port: int,
        sender_email: str,
        sender_password: str,
        use_tls: bool = True,
    ):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.use_tls = use_tls

    def send_booking_confirmation(
        self,
        to_email: str,
        customer_name: str,
        movie_title: str,
        theatre_name: str,
        screen_name: str,
        show_datetime: str,
        seat_labels: list[str],
        total_amount: float,
        booking_id: int,
        transaction_ref: str | None = None,   # ✅ FIXED
    ) -> tuple[bool, str]:

        # Basic validation
        if not to_email:
            return False, "Recipient email is required."

        if not seat_labels:
            return False, "No seats provided."

        subject = f"Booking Confirmation - {movie_title}"
        seats_text = ", ".join(seat_labels)

        transaction_line = (
            f"Transaction Reference: {transaction_ref}\n"
            if transaction_ref else ""
        )

        body = f"""
Hello {customer_name},

Your movie booking has been confirmed.

Booking Details:
----------------------------------------
Booking ID: {booking_id}
{transaction_line}Movie: {movie_title}
Theatre: {theatre_name}
Screen: {screen_name}
Show Time: {show_datetime}
Seats: {seats_text}
Total Paid: ${total_amount:.2f}
----------------------------------------

Thank you for booking with us.
Enjoy your movie!

Regards,
Cinema Booking Team
""".strip()

        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = self.sender_email
        msg["To"] = to_email
        msg.set_content(body)

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()

                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)

            return True, "Email sent successfully."

        except Exception as exc:
            return False, f"Failed to send email: {exc}"