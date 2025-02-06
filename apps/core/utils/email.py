import datetime
import os
from typing import List, Optional, Any

from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from pydantic import BaseModel, EmailStr


email_host = os.environ.get("EMAIL_HOST_USER")
msdat_admin = os.environ.get("MSDAT_ADMIN")


class EmailContent(BaseModel):
    """
    The email content base model. This is used to create the email content.
    """

    title: str
    recipients: List[EmailStr]
    subject: str
    username: Optional[str] = None
    email: Optional[EmailStr]
    body: str
    dataframe: Optional[str]
    attachments: Optional[List[Any]]
    has_action: bool
    action_name: Optional[str]
    action_link: Optional[str]


class RequestDashboardEmailContent(EmailContent):
    link: str
    creator_name: str
    creator_email: str
    description: str
    reason: str
    category: str
    dashboard_name: str


class InvitationEmailContent(EmailContent):
    token: str


def send_mail(email_content: EmailContent, template_name: str):
    """
    Send an email using the specified template.
    """
    subject = email_content.subject
    html_message = render_to_string(f"{template_name}.html", email_content.model_dump())
    plain_message = strip_tags(html_message)
    from_email = f"DMI Team <{email_host}>"
    to = email_content.recipients

    email = EmailMultiAlternatives(
        subject,
        plain_message,
        from_email,
        to,
    )
    email.attach_alternative(html_message, "text/html")

    if email_content.attachments:
        for attachment in email_content.attachments:
            email.attach_file(attachment)
    email.send()


class EmailManger:

    def send_file_uploaded_email(self, id, name, file_type, dataframe):
        """Email method to notify the team when file upload is successful"""

        message = f"""
            A new file upload has been submitted on MSDAT through DMI. 
            The name of the file upload is {name}, with id {id} of type {file_type}. 
            This file was uploaded at {datetime.datetime.now().strftime("%B %d, %Y")}.
        """
        content = EmailContent(
            title="File Upload Successful",
            recipients=[msdat_admin, "datageneral@e4email.net"],
            subject="File Upload",
            username="MSDAT Team",
            dataframe=dataframe,
            body=message,
            has_action=False,
        )
        send_mail(content, template_name="file_uploaded_email")

    def send_file_normalization_successful_email(self, id, name, file_type, dataframe):
        """Email method to notify the team when file normalization is successful"""

        message = f"""
            File upload normalization is complete and is ready to be pushed to MSDAT database through DMI. 
            The name of the file upload is {name}, with id {id} of type {file_type}. 
            This file was normalized at {datetime.datetime.now().strftime("%B %d, %Y")}.
        """

        content = EmailContent(
            title="File Normalization Successful",
            recipients=[msdat_admin, "datageneral@e4email.net"],
            subject="File Normalization",
            username="MSDAT Team",
            dataframe=dataframe,
            body=message,
            has_action=False,
        )
        send_mail(content, template_name="file_normalization_successful_email")

    def send_file_normalization_unsuccessful_email(
        self, id, name, file_type, error, dataframe
    ):
        """Email method to notify the team when file normalization is unsuccessful"""

        message = f"""
            Normalization failed due to error: {error}. 
            The name of the file upload is {name}, with id {id} of type {file_type}. 
            This file was uploaded at {datetime.datetime.now().strftime("%B %d, %Y")}.
        """

        content = EmailContent(
            title="File Normalization Unsuccessful",
            recipients=[msdat_admin, "datageneral@e4email.net"],
            subject="File Normalization",
            username="MSDAT Team",
            dataframe=dataframe,
            body=message,
            has_action=False,
        )
        send_mail(content, template_name="file_normalization_unsuccessful_email")

    def send_file_push_successful_email(self, id, name, file_type, dataframe):
        """Email method to notify the team when file push is successful"""

        message = f"""
            A new file upload has been pushed to the MSDAT database through DMI. 
            The name of the file upload is {name}, with id {id} of type {file_type}. 
            This file was uploaded at {datetime.datetime.now().strftime("%B %d, %Y")}.
        """

        content = EmailContent(
            title="File Push Successful",
            recipients=[msdat_admin, "datageneral@e4email.net"],
            subject="File Pushed",
            username="MSDAT Team",
            dataframe=dataframe,
            body=message,
            has_action=False,
        )
        send_mail(content, template_name="file_push_successful_email")

    def send_file_push_unsuccessful_email(self, id, name, file_type, error, dataframe):
        """Email method to notify the team when file push is unsuccessful"""

        message = f"""
            A new file upload failed to push to MSDAT database through DMI due to error: {error}. 
            The name of the file upload is {name}, with id {id} of type {file_type}. 
            This file was uploaded at {datetime.datetime.now()}.
        """

        content = EmailContent(
            title="File Push Unsuccessful",
            recipients=[msdat_admin, "datageneral@e4email.net"],
            subject="File Pushed",
            username="MSDAT Team",
            dataframe=dataframe,
            body=message,
            has_action=False,
        )
        send_mail(content, template_name="file_push_unsuccessful_email")

    def send_password_reset_token_email(self, id, name, email, token):
        """
        Send an email to a user containing their password reset link and token
        """

        message = f"""
            Someone, hopefully you has requested to change their password 
            If you didn't initiate this process Kindly Ignore. Else copy the 
            Activation code "{token}\" and click the button below """

        content = EmailContent(
            title="Password Reset Token",
            recipients=[email],
            subject="Password Reset",
            username=name,
            body=message,
            has_action=True,
            token=token,
            action_name="Reset Password",
            action_link="http://208.87.128.190:3032/#/login",
        )
        send_mail(content, template_name="base")

    def send_request_dashboard_email(self, sender, instance, created, **kwargs):
        """
        Send an email to a data-team to verify the dashboard
        """
        message = f"""
            Dear Donsuur/ Ganiyat,\n
            Kindly review the details of this new custom dashboard that was created:\n

            Creator of dashboard: {instance.name}\n
            Email: {instance.email}\n
            Description: {instance.description}\n
            Reason for creation: {instance.reason}\n
            Category: {instance.category}\n
            Dashboard name: {instance.name}\n
            Link: {instance.name}\n

            Approval is sought before making it public.

            Best,
            Ehealth4Everyone

            """

        content = RequestDashboardEmailContent(
            title="Action Required: Review and Approve New Public Dashboard",
            recipients=[
                "doosuur.gyer@e4email.net",
                "ganiyat.issa-onilu@e4email.net",
                "crystal.okedi@e4email.net",
            ],
            subject="Request Dashboard",
            username=instance.name,
            body=message,
            has_action=True,
            token="token",
            action_name="confirm dashboard",
            action_link="http://172.93.52.240:3001/api/request_dashboard/{id}/confirm_dashboard/",
            link=instance.link,
            creator_name=instance.name,
            creator_email=instance.email,
            description=instance.description,
            reason=instance.reason,
            category=instance.category,
            dashboard_name=instance.name_of_dashboard,
        )
        send_mail(content, template_name="base")

    def notify_request_dashboard_email(self, id, name, email):
        message = f"""
            Your custom dashboard has been created"""

        content = EmailContent(
            title="Dashboard Request",
            recipients=[email],
            subject="Custom Request Dashboard",
            username=name,
            body=message,
        )
        send_mail(content, template_name="base")

    def invitation_email(self, id, name, email):
        message = f"""
            You are invited to join DMI, click the link to complete registration.
            Registration link expires in 7 days
            """

        content = InvitationEmailContent(
            title="Invitation Request",
            recipients=[email],
            subject="Invitation to Join DMI",
            body=message,
        )
        send_mail(content, template_name="invitation_email")


def send_invitation_email(email: str, key: str):
    template = get_template("invitation_email.html")
    message = f"""
            You are invited to join DMI, click the link to complete registration.
            Registration link expires in 7 days
            """
    mail_context = {
        "username": email,
        "token": key,
        "message": message,
        "title": "Invitation Request",
        "link": "front end link",
    }
    message_content = template.render(mail_context)

    subject = "Invitation to Join DMI"
    recipients = [email]
    email_message = EmailMessage(
        subject,
        message_content,
        "pywebdevs@e4email.net",
        recipients,
    )
    email_message.content_subtype = "html"
    email_message.send()
