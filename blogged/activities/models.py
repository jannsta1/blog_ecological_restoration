from blog.models import Post
from django.db import models
from polymorphic.models import PolymorphicModel

################################################################
# Tree Models
################################################################


class TreeSpecies(models.Model):
    # TODO: make primary key a letter code?: https://www.forestresearch.gov.uk/tools-and-resources/tree-species-database/
    common_name = models.CharField(max_length=100)
    genus = models.CharField(max_length=100)
    specific_epithet = models.CharField(max_length=100)


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


class Activity(PolymorphicModel):
    class ActivityType(models.IntegerChoices):
        GENERIC = 0, "Generic Activity"
        TREE_PLANTING_SESSION = 1, "Tree Planting"
        VOLE_GUARD_REMOVAL = 2, "Vole Guard Removal"
        INVASIVE_SPECIES_REMOVAL = 3, "Invasive Species Removal"
        TRAINING = 4, "Training Exercise"
        WORKSHOP = 5, "Workshop"
        SURVEY = 6, "Surveying"

    # Note: Using PROTECT on Post to avoid accidental deletion of posts with activities
    #       also tried "SET_DEFAULT" but this lead to a lot of dangling activities - at least during development
    post = models.ForeignKey(
        Post, null=True, on_delete=models.PROTECT, related_name="activities"
    )
    location = models.CharField(max_length=2, null=True, choices=Location.choices)

    activity_type = ActivityType.GENERIC
    hours_spent = models.FloatField(null=True, default=0.0) # TODO : we don't want null here, remove it


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
    area_covered = models.FloatField()  # in square meters
    plastic_removed = models.FloatField(null=True)  # in kilograms
    trees_liberated = models.IntegerField(null=True)
    gps_track = models.JSONField(
        null=True
    )  # TODO: define a GPS data model - JSON for flexibility or create a lat/lon/alt model?


class ActivityInvasiveSpeciesRemoval(Activity):
    activity_type = Activity.ActivityType.INVASIVE_SPECIES_REMOVAL
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
