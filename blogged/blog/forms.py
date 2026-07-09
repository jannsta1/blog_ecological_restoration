import json
from datetime import datetime

from activities.models import Activity
from activities.models import Location
from activities.models import TransportCar
from activities.models import TransportPublic
from activities.models import TreeSpecies
from activities.models import TreePlanting
from django import forms
from django.db.models.functions import Lower
from dal import autocomplete
from django.forms import BaseInlineFormSet
from django.forms import ClearableFileInput
from django.forms import FileField
from django.forms import FileInput
from django.forms import inlineformset_factory
from django.forms import ModelForm
from django.forms import ModelMultipleChoiceField
from django.forms import NumberInput
from django.forms import Textarea
from django.forms import TextInput
from django.forms.formsets import DELETION_FIELD_NAME

from .models import GpsCoordinates
from .models import Images
from .models import Organisation
from .models import Post
from .models import Videos


class PostForm(ModelForm):
    organisation_tags = ModelMultipleChoiceField(
        queryset=Organisation.objects.all(),
        required=False,
        widget=autocomplete.ModelSelect2Multiple(
            url="organisation-tag-autocomplete",
            attrs={
                "data-html": True,
                "class": "select-generic block w-full",
            },
        ),
        # label='My activity label'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.is_bound and not self.initial.get("date") and not self.instance.pk:
            self.initial["date"] = datetime.today().date()

    class Meta:
        model = Post
        fields = ("title", "date", "content", "organisation_tags")
        widgets = {
            "title": TextInput(attrs={"class": "form-text-field block w-full"}),
            # 'date': DatePickerInput(),
            "date": TextInput(
                attrs={"type": "date", "class": "form-text-field block w-full"}
            ),
            # 'date': TextInput(attrs={'class': 'flatpickr block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring focus:ring-indigo-200 focus:ring-opacity-50',
            #                          'placeholder': 'YYYY-MM-DD'}),
            "content": Textarea(attrs={"class": "form-text-field block w-full"}),
        }
        required_fields = ["title", "date", "content"]


class PostStageOneForm(PostForm):
    class Meta(PostForm.Meta):
        fields = ("title", "date", "organisation_tags")


class PostContentForm(PostForm):
    class Meta(PostForm.Meta):
        fields = ("content",)


class PostTransportForm(forms.Form):
    TRAVEL_OPTION_CAR = "car"
    TRAVEL_OPTION_PUBLIC = "public"
    TRAVEL_OPTION_WALKING = "walking"

    TRAVEL_OPTION_CHOICES = (
        ("", "Select travel option"),
        (TRAVEL_OPTION_CAR, "Car"),
        (TRAVEL_OPTION_PUBLIC, "Public transport"),
        (TRAVEL_OPTION_WALKING, "Walking"),
    )

    travel_option = forms.ChoiceField(
        choices=TRAVEL_OPTION_CHOICES,
        required=False,
        widget=forms.Select(attrs={"class": "form-text-field block w-full"}),
    )
    distance = forms.FloatField(
        required=False,
        min_value=0,
        widget=NumberInput(attrs={"class": "form-text-field block w-full"}),
    )
    carbon_offset = forms.BooleanField(required=False)
    powertrain = forms.ChoiceField(
        choices=TransportCar.Powertrain.choices,
        required=False,
        widget=forms.Select(attrs={"class": "form-text-field block w-full"}),
    )
    passengers = forms.IntegerField(
        required=False,
        min_value=0,
        widget=NumberInput(attrs={"class": "form-text-field block w-full"}),
    )
    public_type = forms.ChoiceField(
        choices=TransportPublic.Type.choices,
        required=False,
        widget=forms.Select(attrs={"class": "form-text-field block w-full"}),
    )

    def clean(self):
        cleaned_data = super().clean()
        travel_option = cleaned_data.get("travel_option")
        distance = cleaned_data.get("distance")

        if not travel_option:
            return cleaned_data

        if distance is None:
            self.add_error("distance", "Distance is required for transport entries.")

        if travel_option == self.TRAVEL_OPTION_CAR:
            if not cleaned_data.get("powertrain"):
                self.add_error("powertrain", "Select a powertrain for car travel.")
            if cleaned_data.get("passengers") is None:
                self.add_error("passengers", "Enter passenger count for car travel.")

        if travel_option == self.TRAVEL_OPTION_PUBLIC and not cleaned_data.get(
            "public_type"
        ):
            self.add_error("public_type", "Select a public transport type.")

        return cleaned_data


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
            latitude = clean_data.get("latitude")
            longitude = clean_data.get("longitude")
            altitude = clean_data.get("altitude")

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
    fields=["latitude", "longitude", "altitude"],
    widgets={
        "latitude": NumberInput(attrs={"class": "form-text-field"}),
        "longitude": NumberInput(attrs={"class": "form-text-field"}),
        "altitude": NumberInput(attrs={"class": "form-text-field"}),
    },
    extra=1,
    can_delete=True,
    formset=GpsInlineFormSet,
)


class ImageInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()

        if any(self.errors):
            return

        has_image = False
        has_main_image = False

        for form in self.forms:
            if not hasattr(form, "cleaned_data"):
                continue

            cleaned_data = form.cleaned_data
            if cleaned_data.get(DELETION_FIELD_NAME):
                continue

            image = cleaned_data.get("image") or getattr(form.instance, "image", None)
            if not image:
                continue

            has_image = True
            if cleaned_data.get("is_main_image"):
                has_main_image = True

        if has_image and not has_main_image:
            raise forms.ValidationError(
                "Select at least one main image before saving or publishing."
            )

    def clean_caption(self):
        pass


ImageFormSet = inlineformset_factory(
    Post,
    Images,
    fields=["image", "caption", "is_main_image"],
    widgets={
        "caption": Textarea(attrs={"class": "form-text-field", "rows": 3}),
        "image": FileInput(attrs={"class": "hidden"}),
    },
    extra=1,
    can_delete=True,
    formset=ImageInlineFormSet,
)


VideoFormSet = inlineformset_factory(
    Post,
    Videos,
    fields=["video", "caption"],
    widgets={
        "caption": Textarea(attrs={"class": "form-text-field", "rows": 3}),
        "video": FileInput(attrs={"class": "hidden", "accept": "video/*"}),
    },
    extra=1,
    can_delete=True,
)

_GPS_TRACK_WIDGET = Textarea(
    attrs={
        "class": "form-text-field block w-full font-mono text-xs",
        "rows": 3,
        "placeholder": '{"type": "LineString", "coordinates": [[lon, lat, alt], ...]}',
    }
)


class PostActivityForm(forms.Form):
    ACTIVITY_TYPE_CHOICES = [("", "Select activity type")] + [
        (choice[0], choice[1]) for choice in Activity.ActivityType.choices
    ]

    activity_type = forms.ChoiceField(
        choices=ACTIVITY_TYPE_CHOICES,
        required=False,
        widget=forms.Select(
            attrs={
                "class": "form-text-field block w-full",
                "id": "activity-type-select",
            }
        ),
    )
    location = forms.ChoiceField(
        choices=[("", "Select location")] + list(Location.choices),
        required=False,
        widget=forms.Select(attrs={"class": "form-text-field block w-full"}),
    )
    hours_spent = forms.FloatField(
        required=False,
        min_value=0,
        widget=NumberInput(attrs={"class": "form-text-field block w-full"}),
    )

    # ── Vole Guard Removal ───────────────────────────────────────────────────
    area_covered = forms.FloatField(
        required=False,
        min_value=0,
        label="Area covered (m²)",
        widget=NumberInput(attrs={"class": "form-text-field block w-full"}),
    )
    plastic_removed = forms.FloatField(
        required=False,
        min_value=0,
        label="Plastic removed (kg)",
        widget=NumberInput(attrs={"class": "form-text-field block w-full"}),
    )
    trees_liberated = forms.IntegerField(
        required=False,
        min_value=0,
        label="Trees liberated",
        widget=NumberInput(attrs={"class": "form-text-field block w-full"}),
    )
    vgr_gps_track = forms.CharField(
        required=False,
        label="GPS track (JSON)",
        widget=_GPS_TRACK_WIDGET,
    )

    # ── Tree Guard Removal ───────────────────────────────────────────────────
    tubes_removed = forms.IntegerField(
        required=False,
        min_value=0,
        label="Tubes removed",
        widget=NumberInput(attrs={"class": "form-text-field block w-full"}),
    )
    tube_weight_g = forms.FloatField(
        required=False,
        min_value=0,
        label="Tube weight (g)",
        widget=NumberInput(attrs={"class": "form-text-field block w-full"}),
    )
    tgr_gps_track = forms.CharField(
        required=False,
        label="GPS track (JSON)",
        widget=_GPS_TRACK_WIDGET,
    )

    # ── Invasive Species Removal ─────────────────────────────────────────────
    species_removed = forms.ModelChoiceField(
        queryset=TreeSpecies.objects.order_by(
            Lower("genus"),
            Lower("specific_epithet"),
            Lower("subspecies"),
            Lower("common_name"),
        ),
        required=False,
        label="Species removed",
        widget=forms.Select(attrs={"class": "form-text-field block w-full"}),
    )
    quantity_removed = forms.FloatField(
        required=False,
        min_value=0,
        label="Quantity removed",
        widget=NumberInput(attrs={"class": "form-text-field block w-full"}),
    )
    isr_gps_track = forms.CharField(
        required=False,
        label="GPS track (JSON)",
        widget=_GPS_TRACK_WIDGET,
    )

    # ── Tree Planting Session ────────────────────────────────────────────────
    tps_notes = forms.CharField(
        required=False,
        max_length=200,
        label="Notes",
        widget=TextInput(attrs={"class": "form-text-field block w-full"}),
    )
    tps_species = forms.ModelChoiceField(
        queryset=TreeSpecies.objects.order_by(
            Lower("genus"),
            Lower("specific_epithet"),
            Lower("subspecies"),
            Lower("common_name"),
        ),
        required=False,
        label="Species planted",
        widget=forms.Select(attrs={"class": "form-text-field block w-full"}),
    )
    tps_quantity = forms.IntegerField(
        required=False,
        min_value=1,
        label="Quantity planted",
        widget=NumberInput(attrs={"class": "form-text-field block w-full"}),
    )
    tps_planting_style = forms.ChoiceField(
        choices=TreePlanting.PlantingStyle.choices,
        required=False,
        label="Planting style",
        widget=forms.Select(attrs={"class": "form-text-field block w-full"}),
    )
    tps_gps_data = forms.CharField(
        required=False,
        label="Tree planting GPS data (JSON)",
        widget=_GPS_TRACK_WIDGET,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        initial_species = self.initial.get("tps_species")
        if isinstance(initial_species, str) and initial_species.strip():
            match = TreeSpecies.objects.filter(common_name=initial_species).first()
            if match is not None:
                self.initial["tps_species"] = match.pk

    def _parse_gps_track(self, field_name):
        raw = self.cleaned_data.get(field_name, "").strip()
        if not raw:
            return None
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            self.add_error(field_name, "Enter valid JSON for the GPS track.")
            return None

    def clean(self):
        cleaned_data = super().clean()
        activity_type = cleaned_data.get("activity_type")
        if not activity_type:
            return cleaned_data

        activity_type_int = int(activity_type)

        if activity_type_int == Activity.ActivityType.VOLE_GUARD_REMOVAL:
            if cleaned_data.get("area_covered") is None:
                self.add_error("area_covered", "Area covered is required.")
            self._parse_gps_track("vgr_gps_track")

        elif activity_type_int == Activity.ActivityType.TREE_GUARD_REMOVAL:
            self._parse_gps_track("tgr_gps_track")

        elif activity_type_int == Activity.ActivityType.INVASIVE_SPECIES_REMOVAL:
            if not cleaned_data.get("species_removed"):
                self.add_error("species_removed", "Species is required.")
            if cleaned_data.get("quantity_removed") is None:
                self.add_error("quantity_removed", "Quantity removed is required.")
            self._parse_gps_track("isr_gps_track")

        elif activity_type_int == Activity.ActivityType.TREE_PLANTING_SESSION:
            if not cleaned_data.get("tps_species"):
                self.add_error("tps_species", "Species planted is required.")
            if cleaned_data.get("tps_quantity") is None:
                self.add_error("tps_quantity", "Quantity planted is required.")
            if not cleaned_data.get("tps_planting_style"):
                self.add_error("tps_planting_style", "Planting style is required.")
            self._parse_gps_track("tps_gps_data")

        return cleaned_data
