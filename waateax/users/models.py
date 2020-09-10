from django.contrib.auth.models import AbstractUser
from django.db.models import CharField, BooleanField, IntegerField
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """Default user for waateax."""

    #: First and last name do not cover name patterns around the globe
    name = CharField(_("Name of User"), blank=True, max_length=255)
    mobile_phone = CharField(_("Mobile phone number (format: 41798257004)"), blank=True, max_length=255)
    active = BooleanField(default=True)

    def get_absolute_url(self):
        """Get url for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"username": self.username})
