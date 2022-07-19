from dataclasses import fields
from rest_framework.serializers import ModelSerializer
from .models import Champ, Filtre, Modele, User
class UserSerializer(ModelSerializer):
    class Meta:
        model=User
        fields = ['id','first_name','last_name', 'email', 'password']
        extra_kwargs = {
                'password':{'write_only':True}
            }
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance

class ChampsSerializer(ModelSerializer):
    class Meta:
        model=Champ
        fields = ['id','id_modele','name','contenu','id_user']  
        
class FiltreSerializer(ModelSerializer):
    class Meta:
        model=Filtre
        fields = ['id','id_modele','contenu','img','id_user'] 


class ModeleSerializer(ModelSerializer):
    class Meta:
        model=Modele
        fields = ['id','name','nbrchamps','id_user']        
    