
import time

import pyotp
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import bs4
from django.core.mail import send_mail
from .find_in_rimnow import find_contenu
from .find_in_ami import find_contenu_ami
import random
import string
from .authentication import JWTAuthentication, create_access_token, create_refresh_token, decode_refresh_token
from .serializers import ChampsSerializer, FiltreSerializer, ModeleSerializer, UserSerializer
from rest_framework.views import APIView
from rest_framework.response import Response

from rest_framework import exceptions
from .models import Champ, Filtre, Modele, Reset, User, UserToken
import datetime
class RegisterAPIView(APIView):
    def post(self, request):
        data=request.data
        if data['password']!=data['password_confirm']:
            raise exceptions.APIException('Le mot de passe est incorrecte')
        serializer=UserSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
class LoginAPIView(APIView):
    def post(self, request):
        email=request.data['email']
        password=request.data['password']
        user = User.objects.filter(email=email).first()
        if user is None:
            raise exceptions.AuthenticationFailed('Le Nom du user est invalide')
        if not user.check_password(password):
            raise exceptions.AuthenticationFailed('Le Mot de passe du user est invalide')
        if user.tfa_secret:
            return Response({
                'id':user.id
            }) 
        secret= pyotp.random_base32()
        otpauth_url = pyotp.totp.TOTP(secret).provisioning_uri(issuer_name="My App")
        return Response({
            'id':user.id,
            'secret':secret,
            'otpauth_url':otpauth_url
        })

class TwoFactorAPIView(APIView):
    def post(self,request):
        id = request.data['id']
        user= User.objects.filter(pk=id).first()
        if not user:
            raise exceptions.AuthenticationFailed('Les attributs du user invalident')
        secret=user.tfa_secret if user.tfa_secret !='' else request.data['secret']
        if not pyotp.TOTP(secret).verify(request.data['code']):
            raise exceptions.AuthenticationFailed('Les attributs du user invalident')
        if  user.tfa_secret=='':
            user.tfa_secret=secret
            user.save()
        access_token = create_access_token(id)
        refresh_token = create_refresh_token(id)
        UserToken.objects.create(
            user_id = id,
            token = refresh_token,
            expired_at=datetime.datetime.utcnow() + datetime.timedelta(days=7)
        ) 

        response =Response()
        response.set_cookie(key='refresh_token', value=refresh_token, httponly=True)
        response.data={
            'token':access_token
        }
        return response 

class UserAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    def get(self, request):
        return Response(UserSerializer(request.user).data)
class RefreshAPIView(APIView):
    def post(self, request):
        refresh_token = request.COOKIES.get('refresh_token')
        id = decode_refresh_token(refresh_token)
        if not UserToken.objects.filter(
            user_id=id,
            token =refresh_token,
            expired_at__gt =datetime.datetime.now(tz=datetime.timezone.utc)
        ).exists():
            raise exceptions.AuthenticationFailed('Non Identifie')
        access_token = create_access_token(id)

        return Response({
            'token':access_token
        })
class LogoutAPIView(APIView):
    def post(self, request):
        refresh_token = request.COOKIES.get('refresh_token')

        UserToken.objects.filter(token=refresh_token).delete()
        response =Response()
        response.delete_cookie(key='refresh_token')
        response.data={
            'message':'succes'
        }
        return response
class ForgotAPIView(APIView):
    def post(self, request):
        email=request.data['email']
        token = ''.join(random.choice(string.ascii_lowercase+string.digits) for _ in range(10))
        Reset.objects.create(
            email=email,
            token= token
        )
        url= 'http://localhost:8080/reset/'+token
        send_mail(
            subject='Ajoutez votre nouveau mot de passe',
            message='Clickez Ici : <a href="%s">\nPour Ajoutez votre nouveau mot de passe</a>' %url,
            from_email='from@exemple.com',
            recipient_list=[email]
        ) 

        return Response({
            'message':'succes'
        })

class ResetAPIView(APIView):
    def post(self, request):
        data=request.data
        if data['password']!=data['password_confirm']:
            raise exceptions.APIException('Le mot de passe est incorrecte!')
        reset_password = Reset.objects.filter(token = data['token']).first()
        if not reset_password:
            raise exceptions.APIException('Le lien est invalide!')
        user = User.objects.filter(email=reset_password.email).first()
        if not user:
            raise exceptions.APIException('Le user est introuve!')
        user.set_password(data['password'])
        user.save()
        return Response({
            'message': 'succes'
        })



class ModelAPIView(APIView):
    def post(self, request):
      if request.method=='POST':    
        data=request.data        
        serializer=ModeleSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
        
    
    def get(self, request,model):
        if request.method=='GET':
          if model:
            models=Modele.objects.filter(id=model).first()
            serializer=ModeleSerializer(models)   
            return Response(serializer.data)
          else:
            models=Modele.objects.all()

            serializer=ModeleSerializer(models,many=True)   
            return Response(serializer.data)

    def put(self, request):
        if request.method=='PUT':
            id=request.data['id'] 
            model=Modele.objects.filter(pk=id).first()            
            data=request.data        
            serializer=ModeleSerializer(model,data=data)
            if(serializer.is_valid()):
                serializer.save()
                return Response(serializer.data)
            
            return Response(serializer.errors)
    def delete(self, request):
        if request.method=='DELETE':
            id=request.data['id']  
            champs=Champ.objects.filter(id_modele_id=id) 
            filtres=Filtre.objects.filter(id_modele_id=id) 
            for champ in champs:
                    champ.delete()
            for filtre in filtres:
                    filtre.delete()      
            model=Modele.objects.get(pk=id) 
            model.delete()   
            return Response(status=204)

    



class ChampAPIView(APIView):
    def post(self, request):
        data=request.data  
        serializer=ChampsSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def put(self, request):
          if request.method=='PUT':
            id=request.data.get('id')
            champ=Champ.objects.get(pk=id)  
            data=request.data    
            serializer=ChampsSerializer(champ,data=data)
            serializer.is_valid(raise_exception=True)
            if(serializer.is_valid()):
                serializer.save()
                return Response(serializer.data)
    def get(self, request):
        if not  request.data:  
                champs= Champ.objects.all()   
                serializer=ChampsSerializer(champs,many=True)
                return Response(serializer.data)
        elif request.data['id']:
             id=request.data['id']
             champ=Champ.objects.filter(pk=id).first()
             serializer=ChampsSerializer(champ)
             return Response(serializer.data)


    def delete(self, request):
         if request.method=='DELETE':
            id=request.data['id']  
            champ=Champ.objects.get(pk=id) 
            champ.delete()   
            return Response(status=204)
class ListFiltreAPIView(APIView):
    def get(self, request,user,model):
        if request.method=='GET':
            if model:
                filtres= Filtre.objects.filter(id_modele_id=model,id_user_id=user)
                serializer=FiltreSerializer(filtres,many=True)
                return Response(serializer.data)
            else:
                filtres= Filtre.objects.filter(id_user_id=user)
                serializer=FiltreSerializer(filtres,many=True)
                return Response(serializer.data)

class FindFiltresAPIView(APIView):
    def get(self, request):
       find_contenu() 
       return Response()
class findAmiAPIView(APIView):
    def post(self, request,user):
        if request.method =='POST':
            
            find_contenu_ami(id_user=user)
            return Response()

