from pickle import NONE
from xml.parsers.expat import model
from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    username=NONE
    tfa_secret = models.CharField(max_length=255, default='')
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

class UserToken(models.Model):
    user_id = models.IntegerField()
    token = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    expired_at = models.DateTimeField()
class Reset(models.Model):
    email = models.CharField(max_length=255)
    token = models.CharField(max_length=255, unique=True)
class Modele(models.Model):
    id_user=models.ForeignKey(User,on_delete=models.CASCADE,default=1)
    name = models.TextField(max_length=255, unique=True)
    nbrchamps = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Champ(models.Model):
    id_user=models.ForeignKey(User,on_delete=models.CASCADE,default=1)
    id_modele=models.ForeignKey(Modele,on_delete=models.CASCADE)
    name = models.CharField(max_length=255, unique=True)
    contenu = models.CharField(max_length=255, unique=True)

class Filtre(models.Model):
    id_user=models.ForeignKey(User,on_delete=models.CASCADE,default=1)
    id_modele=models.ForeignKey(Modele,on_delete=models.CASCADE)
    contenu = models.TextField(unique=True)
    img= models.URLField(default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

