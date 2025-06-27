from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('', views.UserListCreateView.as_view(), name='user-list-create'),
    path('<int:pk>/', views.UserDetailView.as_view(), name='user-detail'),
    path('api-key/info/', views.api_key_info, name='api-key-info'),
    path('api-key/validate/', views.validate_api_key, name='api-key-validate'),
]
