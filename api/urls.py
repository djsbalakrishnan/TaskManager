from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views


router = DefaultRouter()
router.register('todos', views.ToDoViewSet)

urlpatterns = [
    path('create_user/', views.CreateUserView.as_view(), name="create_user"),
    path('create_user_token/', views.CreateUserAuthTokenView.as_view(), name="create_user_token"),
    path('manage_user/', views.ManageUserView.as_view(), name="manage_user"),
    path('', include(router.urls)),
]
