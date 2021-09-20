from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from rest_framework import viewsets

from users.serializers import UserSerializer, AuthTokenSerializer
from django.contrib.auth import get_user_model

class CreateUserView(generics.CreateAPIView):
    """ Create a new user """
    
    serializer_class = UserSerializer



class CreateTokenView(ObtainAuthToken):
    """ Create new auth token for user """

    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer
    #permission_classes = [permissions.IsAuthenticated]    