from django.forms import Form, ModelForm, TextInput, ClearableFileInput, FileField, Textarea, DateField, DateInput, CharField, FileInput, ClearableFileInput, fields, NumberInput
from django.template.defaultfilters import slugify
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory, BaseInlineFormSet
from django.forms.formsets import DELETION_FIELD_NAME
from formset.widgets import DatePicker
from django_flatpickr.widgets import DatePickerInput


from datetime import datetime

from .models import Comment, MediaAttachment, Post, Images, GpsCoordinates



class CommentForm(ModelForm):    
    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'class': 'w-full py-4 bg-gray-100'})
        self.fields['content'].widget.attrs.update({'class': 'w-full py-4 bg-gray-100'})

    class Meta:
        model = Comment
        fields = ['name', 'content']



class PostForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)        
        self.initial['date'] = datetime.today().date()

    class Meta:
        model = Post
        fields = ('title', 'date', 'content')
        widgets = {
            'title': TextInput(attrs={'class': "form-text-field block w-full"}),
            # 'date': DatePickerInput(),
            'date': TextInput(attrs={'type': 'date', 'class': "form-text-field block w-full"}),
            # 'date': TextInput(attrs={'class': 'flatpickr block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring focus:ring-indigo-200 focus:ring-opacity-50',
            #                          'placeholder': 'YYYY-MM-DD'}),
            'content': Textarea(attrs={'class': "form-text-field block w-full"}),            
        }


class MultipleFileInput(ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result
    
class LocationForm(ModelForm):
    class Meta:
        model = GpsCoordinates
        fields = ("latitude", "longitude", "altitude")





class GpsInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
                
        element_idxs_to_clean = []
        observed_coordinates = []

        for idx, clean_data in enumerate(self.cleaned_data):
            latitude = clean_data.get('latitude')
            longitude = clean_data.get('longitude')
            altitude = clean_data.get('altitude')

            # NOTE - it seems like empty dictionaries don't get added to the ORM database anyway but we remove this 
            # to keep the cleaned_data to represent what is submitted to the database.
            if not any((latitude, longitude, altitude)):
                element_idxs_to_clean.append(idx)
                self.forms[idx].cleaned_data[DELETION_FIELD_NAME] = True
                continue

            # remove duplicate elements
            if clean_data in observed_coordinates:
                element_idxs_to_clean.append(idx)
                self.forms[idx].cleaned_data[DELETION_FIELD_NAME] = True
                continue
            else:
                observed_coordinates.append(clean_data)


        # for idx in sorted(element_idxs_to_clean, reverse=True):
        #     print(f"removing the element {self.cleaned_data[idx]}")            
        #     self.forms[idx].cleaned_data[DELETION_FIELD_NAME] = True

        return self.cleaned_data





GpsFormSet = inlineformset_factory(
    Post,
    GpsCoordinates,
    fields=['latitude', 'longitude', 'altitude'],
    widgets={'latitude': NumberInput(attrs={'class': "form-text-field"}),
             'longitude': NumberInput(attrs={'class': "form-text-field"}),
             'altitude': NumberInput(attrs={'class': "form-text-field"}),
            },
    extra=1,
    can_delete=True,
    formset=GpsInlineFormSet,
)


# class ImageForm(ModelForm):
    
#     image = MultipleFileField(label='Select images', required=False)
    
#     class Meta:
#         model = Images
#         fields = ('image', 'caption')
#         widgets = {
#             'caption': Textarea(attrs={'class': 'form-text-field', 'rows': 3}),
#             # 'title': TextInput(attrs={'class': 'w-full py-2 bg-gray-100'}),
#             # 'caption': TextInput(attrs={'class': 'w-full py-2 bg-gray-100'}),
#         }


class ImageInlineFormSet(BaseInlineFormSet):
    def clean(self):
        # super().clean()
                
        pass

    def clean_caption(self):
        pass
   


ImageFormSet = inlineformset_factory(
    Post,
    Images,
    fields=['image', 'caption'],
    widgets={'caption': Textarea(attrs={'class': 'form-text-field', 'rows': 3}),
             'image': FileInput(attrs={'class': 'hidden'})
             },
    extra=1,
    can_delete=True,
    formset=ImageInlineFormSet,
)