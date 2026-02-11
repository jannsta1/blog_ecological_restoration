from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import redirect
from django.shortcuts import reverse
from django.views.generic import FormView
from django.views.generic import TemplateView

from .forms import ContactForm


class SuccessView(TemplateView):
    template_name = "blogcontact/success.html"


class FailureView(TemplateView):
    template_name = "blogcontact/failure.html"


class ContactView(FormView):
    form_class = ContactForm
    template_name = "blogcontact/contact.html"

    def get_success_url(self):
        return reverse("contact-success")

    def get_failure_url(self):
        return reverse("contact-failure")

    def form_valid(self, form):
        email = form.cleaned_data.get("email")
        subject = form.cleaned_data.get("subject")
        message = form.cleaned_data.get("message")

        full_message = f"""
            Received message below from {email}, {subject}
            ________________________


            {message}
            """

        try:
            send_mail(
                subject="Received contact form submission",
                message=full_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.NOTIFY_EMAIL],
            )
            # raise Exception("Test email sending failure")  # TODO - remove this line after testing the email sending failure case
        except Exception as e:
            messages.error(self.request, f"Error sending email: {e}")
            # TODO - make it so that the admin gets an email if the contact form email fails to send? Or some other alert system? Maybe sentry?
            #        https://docs.djangoproject.com/en/6.0/howto/error-reporting/
            # messages.error(self.request, f"Error sending email - admin have been notified and will try to resolve this issue as soon as possible.")
            print(f"Error sending email: {e}")
            return redirect("contact-failure")

        messages.success(
            self.request, "Message Received! We'll respond to you in the next few days."
        )
        #
        return redirect("contact-success")

        # return super(ContactView, self).form_valid(form)
