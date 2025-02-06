from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.core.utils.abstracts import AbstractProfileSettings, AbstractUUID
from apps.core.utils.enums import FarmSizeMeasureEnum, FarmerCategory, PartnerTypeEnum, SellerTypeEnum, UserTypeEnum, GenderEnum, ValidIDType
from apps.core.utils.country.countries import country_codes

class User(AbstractUser, AbstractUUID):
    """
    USER MODELS
    """
    email = models.EmailField(max_length=30, unique=True)
    gender = models.CharField(choices=GenderEnum.choices())
    phone_number = models.CharField(max_length=15)
    type = models.PositiveSmallIntegerField(default=0, choices=UserTypeEnum.choices())
    avatar = models.ImageField(upload_to="profile", null=True, blank=True)
    is_confirmed = models.BooleanField(default=False, blank=True)
    is_accept_terms_and_condition = models.BooleanField(default=False, blank=True)
    country = models.CharField(max_length=30, choices=country_codes, null=True, blank=True)
    state = models.CharField(max_length=255, null=True, blank=True)
    local_govt = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    zip_code = models.CharField(max_length=255, null=True, blank=True)
    town = models.CharField(max_length=255, null=True, blank=True)
    address = models.TextField(default="", null=True, blank=True)
    first_login = models.BooleanField(default=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    date_joined = models.DateTimeField(
        auto_now_add=True, editable=False, null=True, blank=True
    )
    

    class Meta:
        db_table = "users"
        ordering = ("-date_joined",)

    def __str__(self):
        return f"{self.id}"


class PartnerSettings(AbstractProfileSettings):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    organization = models.CharField(max_length=255)
    location = models.CharField(max_length=225)
    business_type = models.CharField(max_length=225, choices=PartnerTypeEnum.choices)
    service = models.CharField(max_length=225)
    


class AgentSettings(AbstractProfileSettings):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    organization = models.CharField(max_length=255)
    years_of_experience = models.IntegerField(min=1)
    area_of_specialization = models.CharField(max_length=225)
    certification = models.CharField(max_length=225)
    
    
class FarmerSettings(AbstractUUID):
    """this model handles farmer settings and profile information
    A single user in later version will be able to have more than one farmer settings which is equivalent to business
    """

    type = models.CharField(
        max_length=50,
        choices=SellerTypeEnum.choices(),
        default=SellerTypeEnum.FARMER,
        null=True,
        blank=True,
    )
    is_verified = models.BooleanField(default=False)
    reg_no = models.CharField(max_length=255, null=True, blank=True)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="seller", null=True, blank=True
    )
    category = models.CharField(
        max_length=200, null=True, blank=True, choices=FarmerCategory.choices()
    )
    
    state = models.CharField(max_length=255, null=True, blank=True)
    country = models.CharField(max_length=30, choices=country_codes, null=True, blank=True)
    local_govt = models.CharField(max_length=255, null=True, blank=True)
    address = models.TextField(default="")
    is_current = models.BooleanField(default=False)
    # crops = models.ManyToManyField(
    #     ProductCategory,
    #     limit_choices_to={"type": "crop"},
    #     blank=True,
    #     related_name="crop_cultivating",
    # )
    # animals = models.ManyToManyField(
    #     ProductCategory, limit_choices_to={"type": "animal"}, blank=True, related_name="animal_rear"
    # )
    farm_size = models.FloatField(default=0, null=True, blank=True)
    farm_size_measurement = models.CharField(
        max_length=20, null=True, blank=True, choices=FarmSizeMeasureEnum.choices()
    )
    disability = models.CharField(max_length=255, null=True, blank=True)
    image = models.ImageField(upload_to="farmer_images", null=True, blank=True)
    is_crop_cultivation = models.BooleanField(default=False, blank=True, null=True)
    is_animal_farming = models.BooleanField(default=False, blank=True, null=True)
    # mode of identification
    means_of_identification_type = models.CharField(
        max_length=50, choices=ValidIDType.choices(), null=True, blank=True
    )
    means_of_identification = models.FileField(upload_to="documents/", null=True, blank=True)
    # bank information
    bank_code = models.CharField(max_length=255, null=True, blank=True)
    bank_name = models.CharField(max_length=255, null=True, blank=True)
    account_number = models.CharField(max_length=255, null=True, blank=True)
    account_name = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        return "{0} {1}".format(str(self.user), str(self.created_at))

    class Meta:
        ordering = ("-created_at",)
        db_table = "farmer_settings"
        verbose_name = "FarmerSetting"
        verbose_name_plural = "FarmerSettings"

    def is_mode_of_identification(self):
        return all([bool(self.means_of_identification), bool(self.means_of_identification_type)])

    def is_farmer_info(self):
        info = [bool(self.user.marital_status), bool(self.user.gender), bool(self.address),
                bool(self.state), bool(self.local_govt)]
        return all(info)

    def is_farm_information(self):
        info = [
            bool(self.type),
            bool(self.business_name),
            bool(self.state),
            bool(self.local_govt),
            bool(self.address)
        ]
        return all(info)