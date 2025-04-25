from django.core.mail import send_mail
from django.conf import settings

class NotificationService:
    
    @staticmethod
    def send_email(subject, message, recipient_list, html_message=None):
        '''
        Sends an email to a list of recipients.

        Parameters:
        subject (str): The subject of the email.
        message (str): The plain text content of the email.
        recipient_list (list): A list of email addresses to send the email to.
        html_message (str, optional): The HTML content of the email. Defaults to None.

        Returns:
        int: The number of successfully delivered messages.
        '''
        return send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            html_message=html_message
        )
    
    @staticmethod
    def send_sms(phone_number, message):
        '''
        Sends an SMS notification to a given phone number.

        Parameters:
        phone_number (str): The phone number to send the SMS to.
        message (str): The content of the SMS message.

        Returns:
        bool: Always returns True for this placeholder implementation.
        '''
        print(f"Sending SMS to {phone_number}: {message}")
        return True
    
    @staticmethod
    def send_in_app_notification(user, message):
        '''
        Creates an in-app notification for a given user.

        Parameters:
        user (User): The user who will receive the in-app notification.
        message (str): The content of the notification.

        Returns:
        Notification: The created Notification object.
        '''
        from apps.notifications.models import Notification
        return Notification.objects.create(user=user, message=message)
