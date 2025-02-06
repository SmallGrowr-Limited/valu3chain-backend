from django.db.models import PositiveSmallIntegerField
from decouple import config


class CustomEnum(object):
    class Enum(object):
        name = None
        value = None
        type = None

        def __init__(self, name, value, type):
            self.key = name
            self.name = name
            self.value = value
            self.type = type

        def __str__(self):
            return self.name

        def __repr__(self):
            return self.name

        def __eq__(self, other):
            if other is None:
                return False
            if isinstance(other, CustomEnum.Enum):
                return self.value == other.value
            raise TypeError

    @classmethod
    def choices(c):
        attrs = [a for a in c.__dict__.keys() if a.isupper()]
        values = [(c.__dict__[v], CustomEnum.Enum(v, c.__dict__[v], c).__str__()) for v in attrs]
        return sorted(values, key=lambda x: x[0])

    @classmethod
    def default(cls):
        """
        Returns default value, which is the first one by default.
        Override this method if you need another default value.
        """
        return cls.choices()[0][0]

    @classmethod
    def field(cls, **kwargs):
        """
        A shortcut for
        Usage:
            class MyModelStatuses(CustomEnum):
                UNKNOWN = 0
            class MyModel(Model):
                status = MyModelStatuses.field(label='my status')
        """
        field = PositiveSmallIntegerField(choices=cls.choices(), default=cls.default(), **kwargs)
        field.enum = cls
        return field

    @classmethod
    def get(c, value):
        if type(value) is int:
            try:
                return [
                    CustomEnum.Enum(k, v, c)
                    for k, v in c.__dict__.items()
                    if k.isupper() and v == value
                ][0]
            except Exception:
                return None
        else:
            try:
                key = value.upper()
                return CustomEnum.Enum(key, c.__dict__[key], c)
            except Exception:
                return None

    @classmethod
    def key(c, key):
        try:
            return [value for name, value in c.__dict__.items() if name == key.upper()][0]
        except Exception:
            return None

    @classmethod
    def name(c, key):
        try:
            return [name for name, value in c.__dict__.items() if value == key][0]
        except Exception:
            return None

    @classmethod
    def get_counter(c):
        counter = {}
        for key, value in c.__dict__.items():
            if key.isupper():
                counter[value] = 0
        return counter

    @classmethod
    def items(c):
        attrs = [a for a in c.__dict__.keys() if a.isupper()]
        values = [(v, c.__dict__[v]) for v in attrs]
        return sorted(values, key=lambda x: x[1])

    @classmethod
    def to_list(c):
        attrs = [a for a, _ in c.choices()]
        return attrs

    @classmethod
    def is_valid_transition(c, from_status, to_status):
        return from_status == to_status or from_status in c.transition_origins(to_status)

    @classmethod
    def transition_origins(c, to_status):
        return to_status

    @classmethod
    def get_name(c, key):
        choices_name = dict(c.choices())
        return choices_name.get(key)



class UserGroupEnum(CustomEnum):
    USER: str = "user"
    PARTNER: str = "partner"
    ADMIN: str = "admin"
    AGENT: str = "agent"

    @classmethod
    def choices(cls):
        return (
            (cls.USER, "User"),
            (cls.PARTNER, "Farmer"),
            (cls.ADMIN, "Admin"),
            (cls.AGENT, "Agent")
        )


class UserTypeEnum(CustomEnum):
    USER: int = 0
    PARTNER: int = 1
    AGENT: int = 2
    ADMIN: int = 3
    
    @classmethod
    def choices(cls):
        return (
            (cls.USER, "User"),
            (cls.PARTNER, "Partner"),
            (cls.AGENT, "Agent")
            (cls.ADMIN, "Admin")
        )
    

class GenderEnum(CustomEnum):
    MALE: str = "male"
    FEMALE: str = "female"

    @classmethod
    def choices(cls):
        return (
            (cls.MALE, "Male")
            (cls.FEMALE, "Female")
        )


class FarmerCategory(CustomEnum):
    BUSINESS = "business"
    SEASONAL = "seasonal"

    @classmethod
    def choices(cls):
        return (
            (cls.BUSINESS, "BUSINESS"),
            (cls.SEASONAL, "SEASONAL"),
        )
        
        
class FarmerType(CustomEnum):
    ANIMAL_REARING = "ANIMAL_REARING"
    CROP_CULTIVATION = "CROP_CULTIVATION"
    ANIMAL_CROP_CULTIVATION = "ANIMAL_CROP_CULTIVATION"

    @classmethod
    def choices(cls):
        return (
            (cls.ANIMAL_REARING, "ANIMAL REARING"),
            (cls.CROP_CULTIVATION, "CROP CULTIVATION"),
            (cls.ANIMAL_CROP_CULTIVATION, "ANIMAL CROP CULTIVATION"),
        )
        

class DisabilityType(CustomEnum):
    DISABLE = "disable"
    NOT_DISABLE = "not_"

    @classmethod
    def choices(cls):
        return (
            (cls.DISABLE, "DISABLE"),
            (cls.NOT_DISABLE, "NOT DISABLE"),
        )
        
class ProductCategoryTypeEnum(CustomEnum):
    CROP = "crop"
    ANIMAL = "animal"
    MACHINE = "machine"

    @classmethod
    def choices(c):
        return (
            (c.CROP, "CROP"),
            (c.ANIMAL, "ANIMAL"),
            (c.MACHINE, "MACHINE"),
        )


class ValidIDFormat(CustomEnum):
    PDF = "pdf"
    DOC = "word coument"

    @classmethod
    def choices(c):
        return (
            (c.PDF, "pdf"),
            (c.DOC, "word document"),
        )


class ValidIDType(CustomEnum):
    INTERNATIONAL_PASSPORT = "international_passport"
    DRIVER_LICENSE = "drivers_licence"
    NIN = "nin"
    VOTERS_CARD = "voters_card"

    @classmethod
    def choices(c):
        return (
            (c.INTERNATIONAL_PASSPORT, "INTERNATIONAL PASSPORT"),
            (c.DRIVER_LICENSE, "DRIVER'S LICENSE"),
            (c.NIN, "NIN"),
            (c.VOTERS_CARD, "VOTERS CARD"),
        )


class FarmSizeMeasureEnum(CustomEnum):
    ACRE = "acre"
    HECTARE = "hectare"
    PLOT = "plot"

    @classmethod
    def choices(c):
        return (
            (c.PLOT, "Plot"),
            (c.ACRE, "Acre"),
            (c.HECTARE, "Hectare"),
        )


class PartnerTypeEnum(CustomEnum):
    INDIVIDUAL = "individual"
    BUSINESS = "business"


class SellerTypeEnum(CustomEnum):
    FARMER = "farmer"
    AGRO_DEALER = "agro_dealer"