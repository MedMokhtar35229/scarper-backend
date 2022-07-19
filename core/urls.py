
from django.urls import path
from .views import ChampAPIView, FindFiltresAPIView, ListFiltreAPIView, ModelAPIView,ForgotAPIView, LoginAPIView,TwoFactorAPIView, LogoutAPIView, RefreshAPIView, RegisterAPIView, ResetAPIView, UserAPIView, findAmiAPIView
urlpatterns = [
    path('register', RegisterAPIView.as_view()),
    path('login', LoginAPIView.as_view()),
    path('user', UserAPIView.as_view()),
    path('refresh', RefreshAPIView.as_view()),
    path('logout', LogoutAPIView.as_view()),
    path('forgot', ForgotAPIView.as_view()),
    path('reset', ResetAPIView.as_view()),
    path('two-factor',TwoFactorAPIView.as_view()),
    path('model/<int:model>',ModelAPIView.as_view()),
    path('model',ModelAPIView.as_view()),

    path('champ',ChampAPIView.as_view()),
    path('liste-filtres/<int:user>/<int:model>',ListFiltreAPIView.as_view()),
    path('find-filtres',FindFiltresAPIView.as_view()),
    path('find-filtres-ami/<int:user>',findAmiAPIView.as_view()),


]