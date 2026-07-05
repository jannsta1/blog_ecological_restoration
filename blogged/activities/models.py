from blog.models import Post
from django.db import models
from polymorphic.models import PolymorphicModel

################################################################
# Tree Models
################################################################

DEFAULT_TREE_WEIGHT_G = 90.0  # in grams, based on the weight of a typical tree guard (https://www.forestresearch.gov.uk/tools-and-resources/tree-species-database/)


class TreeSpecies(models.Model):
    # TODO: make primary key a letter code?: https://www.forestresearch.gov.uk/tools-and-resources/tree-species-database/
    common_name = models.CharField(max_length=100)
    genus = models.CharField(max_length=100)
    specific_epithet = models.CharField(max_length=100)
    subspecies = models.CharField(max_length=100, null=True, blank=True)

    @property
    def botanical_name(self):
        botanical_name = f"{self.genus} {self.specific_epithet}".strip()
        if self.subspecies:
            botanical_name = f"{botanical_name} subsp. {self.subspecies}".strip()

        return botanical_name

    def __str__(self):
        return (
            self.botanical_name
        )  # ensure botanical_name is computed before common_name


################################################################
# Activities Models
################################################################
class Location(models.TextChoices):
    TALLA = (
        "TA",
        "Talla & Gameshope",
    )
    CARRIFRAN = (
        "CA",
        "Carrifran",
    )
    COREHEAD = (
        "CO",
        "Corehead",
    )
    DUNDREGGAN = (
        "DU",
        "Dundreggan",
    )
    PEEBLES_GOLF_COURSE = (
        "PGC",
        "Peebles Golf Course",
    )


class Activity(PolymorphicModel):
    class ActivityType(models.IntegerChoices):
        GENERIC = 0, "Generic Activity"
        TREE_PLANTING_SESSION = 1, "Tree Planting"
        VOLE_GUARD_REMOVAL = 2, "Vole Guard Removal"
        INVASIVE_SPECIES_REMOVAL = 3, "Invasive Species Removal"
        TRAINING = 4, "Training Exercise"
        WORKSHOP = 5, "Workshop"
        SURVEY = 6, "Surveying"
        TREE_GUARD_REMOVAL = 7, "Tree Guard Removal"

    # Note: Using PROTECT on Post to avoid accidental deletion of posts with activities
    #       also tried "SET_DEFAULT" but this lead to a lot of dangling activities - at least during development
    post = models.ForeignKey(
        Post, null=True, on_delete=models.PROTECT, related_name="activities"
    )
    location = models.CharField(max_length=3, null=True, choices=Location.choices)

    activity_type = ActivityType.GENERIC
    marker_background_color = "green"
    marker_border_color = "green"
    marker_glyph_color = "white"
    marker_glyph_text = "🌳"

    @classmethod
    def get_pin_style(cls):
        return {
            "background": cls.marker_background_color,
            "borderColor": cls.marker_border_color,
            "glyphColor": cls.marker_glyph_color,
            "glyphText": cls.marker_glyph_text,
        }

    hours_spent = models.FloatField(
        null=True, default=0.0
    )  # TODO : we don't want null here, remove it


class ActivityTreePlantingSession(Activity):
    """
    ActivityTreePlantingSession - container for multiple TreePlanting entries
    """

    notes = models.CharField(null=True, max_length=200)
    activity_type = Activity.ActivityType.TREE_PLANTING_SESSION


class TreePlanting(models.Model):
    """
    TreePlanting - represents a planting event within a TreePlantingSession
    """

    class PlantingStyle(models.IntegerChoices):
        PLUG = 0, "Plug"
        BAREROOT = 1, "Bare root"

    trees_planted = models.ForeignKey(
        ActivityTreePlantingSession,
        on_delete=models.CASCADE,
        related_name="tree_plantings",
    )
    quantity = models.IntegerField()
    species = models.ForeignKey(
        TreeSpecies, related_name="tree_plantings", on_delete=models.PROTECT
    )
    planting_style = models.IntegerField(
        choices=PlantingStyle.choices, default=PlantingStyle.PLUG
    )
    gps_data = models.JSONField(
        null=True
    )  # TODO: define a GPS data model - JSON for flexibility or create a lat/lon/alt model?


class ActivityVoleGuardRemoval(Activity):
    activity_type = Activity.ActivityType.VOLE_GUARD_REMOVAL
    marker_background_color = "#2563eb"
    marker_border_color = "#1d4ed8"
    marker_glyph_color = "white"
    marker_glyph_text = "♻️"
    area_covered = models.FloatField()  # in square meters
    plastic_removed = models.FloatField(null=True)  # in kilograms
    trees_liberated = models.IntegerField(null=True)
    gps_track = models.JSONField(
        null=True
    )  # TODO: define a GPS data model - JSON for flexibility or create a lat/lon/alt model?


class ActivityTreeGuardRemoval(Activity):
    activity_type = Activity.ActivityType.TREE_GUARD_REMOVAL
    marker_background_color = "#2563eb"
    marker_border_color = "#1d4ed8"
    marker_glyph_color = "white"
    marker_glyph_text = "♻️"
    tubes_removed = models.IntegerField(
        null=True
    )  # number of tree guards touched (removed or adjusted)
    tube_weight_g = models.FloatField(
        default=DEFAULT_TREE_WEIGHT_G
    )  # weight of each tree guard in grams
    gps_track = models.JSONField(
        null=True
    )  # TODO: define a GPS data model - JSON for flexibility or create a lat/lon/alt model?


class ActivityInvasiveSpeciesRemoval(Activity):
    activity_type = Activity.ActivityType.INVASIVE_SPECIES_REMOVAL
    marker_background_color = "#eb4d25"
    marker_border_color = "#d8331d"
    marker_glyph_color = "white"
    marker_glyph_text = "🌱"
    species_removed = models.ForeignKey(TreeSpecies, on_delete=models.PROTECT)
    quantity_removed = models.FloatField()
    gps_track = models.JSONField(
        null=True
    )  # TODO: define a GPS data model - JSON for flexibility or create a lat/lon/alt model?


class ActivityTraining(Activity):
    activity_type = Activity.ActivityType.TRAINING


class ActivityWorkshop(Activity):
    activity_type = Activity.ActivityType.WORKSHOP


class ActivitySurveying(Activity):
    activity_type = Activity.ActivityType.SURVEY


################################################################
# Transport Models
################################################################
# talla: 46.6
# corehead: 74.8
# carrifran: 56.6


class Transport(models.Model):
    # activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name='transport')
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    distance = models.FloatField()
    carbon_offset = models.BooleanField(default=False)

    class Meta:
        abstract = True


class TransportCar(Transport):
    class Powertrain(models.TextChoices):
        ELECTRIC = "E", "Electric"
        HYBRID = "H", "Hybrid"
        GASOLINE = "G", "Gasoline"
        DIESEL = "D", "Diesel"

    passengers = models.IntegerField(default=0)  # passengers (additional to driver)
    powertrain = models.CharField(
        max_length=1, choices=Powertrain.choices, default=Powertrain.ELECTRIC
    )


class TransportPublic(Transport):
    class Type(models.TextChoices):
        BUS = "B", "Bus"
        TRAIN = "T", "Train"

    type = models.CharField(max_length=1, choices=Type.choices, default=Type.BUS)


class TransportWalking(Transport):
    pass  # no additional fields needed for walking, but we can easily add some in the future if needed (e.g. terrain type, elevation gain, etc.)
