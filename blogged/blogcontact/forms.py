from django import forms


class ContactForm(forms.Form):
    # def __init__(self, *args, **kwargs):
    #     super(ContactForm, self).__init__(*args, **kwargs)

    email = forms.EmailField(
        widget=forms.TextInput(
            attrs={"placeholder": "Your e-mail", "class": "w-full p-4 bg-gray-100"}
        )
    )
    subject = forms.CharField(
        widget=forms.TextInput(
            attrs={"placeholder": "Subject", "class": "w-full p-4 bg-gray-100"}
        )
    )
    message = forms.CharField(
        widget=forms.Textarea(
            attrs={"placeholder": "Your message", "class": "w-full p-4 bg-gray-100"}
        )
    )

    # self.fields['name'].widget.attrs.update({'class': 'w-full py-4 bg-gray-100'})
    # self.fields['content'].widget.attrs.update({'class': 'w-full py-4 bg-gray-100'})
