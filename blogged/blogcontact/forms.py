from django import forms


class ContactForm(forms.Form):
    # def __init__(self, *args, **kwargs):
    #     super(ContactForm, self).__init__(*args, **kwargs)

    email = forms.EmailField(
        widget=forms.TextInput(
            attrs={"placeholder": "Your e-mail", "class": "form-text-field block w-full"}
        )
    )
    subject = forms.CharField(
        widget=forms.TextInput(
            attrs={"placeholder": "Subject", "class": "form-text-field block w-full"}
        )
    )
    message = forms.CharField(
        widget=forms.Textarea(
            attrs={"placeholder": "Your message", "class": "form-text-field block w-full"}
        )
    )

    # self.fields['name'].widget.attrs.update({'class': 'w-full py-4 bg-gray-100'})
    # self.fields['content'].widget.attrs.update({'class': 'w-full py-4 bg-gray-100'})
