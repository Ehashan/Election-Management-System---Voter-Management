from django.db import models
from django.contrib.auth.models import User

class VoterProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nic = models.CharField(max_length=20, unique=True)
    mobile_number = models.CharField(max_length=15)
    is_mobile_verified = models.BooleanField(default=False)
    
    # Extended Registration Fields
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, null=True, blank=True)
    election_year = models.CharField(max_length=4, null=True, blank=True)
    admin_district = models.CharField(max_length=50, null=True, blank=True)
    election_district = models.CharField(max_length=50, null=True, blank=True)
    polling_division = models.CharField(max_length=50, null=True, blank=True)
    postal_code = models.CharField(max_length=10, null=True, blank=True)
    grama_niladari_division = models.CharField(max_length=100, null=True, blank=True)
    village_street = models.CharField(max_length=100, null=True, blank=True)
    household = models.CharField(max_length=50, null=True, blank=True)
    face_image = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.user.username

class RegistrationProxy(models.Model):
    """Proxy model for MongoDB Registration collection"""
    # Fields defined for Admin validation only
    user_id = models.IntegerField(primary_key=True) # Fake PK
    nic = models.CharField(max_length=20)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    mobile_number = models.CharField(max_length=15)
    is_mobile_verified = models.BooleanField()
    verified_at = models.DateTimeField()

    class Meta:
        managed = False
        verbose_name = "User Signup"
        verbose_name_plural = "Users (Signup Data)"
        app_label = 'voters'

class VoterProxy(models.Model):
    """Proxy model for MongoDB voters collection"""
    # Fields defined for Admin validation only
    voter_id = models.CharField(max_length=20, primary_key=True)
    nic = models.CharField(max_length=20)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10)
    admin_district = models.CharField(max_length=50)
    election_district = models.CharField(max_length=50)
    polling_division = models.CharField(max_length=50)
    registration_status = models.CharField(max_length=20)
    registered_at = models.DateTimeField()

    class Meta:
        managed = False
        verbose_name = "Voter Registration"
        verbose_name_plural = "Voters (Registration Data)"
        app_label = 'voters'
