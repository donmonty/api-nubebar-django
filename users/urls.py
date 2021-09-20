from django.urls import path, include

from users import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'', views.UserViewSet)

app_name = 'users'

urlpatterns = [
    path('create/', views.CreateUserView.as_view(), name='create'),
    path('token/', views.CreateTokenView.as_view(), name='token'),
    #path('', include(router.urls)),
]