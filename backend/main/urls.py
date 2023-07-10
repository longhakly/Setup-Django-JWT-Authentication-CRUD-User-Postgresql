"""main URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from base import views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('', views.home , name='home'),
    path('admin/', admin.site.urls),
    path('register', views.register_request, name='register_user'),
    path("login", views.login_request, name="login"),
    path("logout", views.logout_request, name= "logout"),
    # path("<str:token>", views.token_request, name= "token_request"),
    path('accounts/', include('django.contrib.auth.urls')),
    path("users/password_reset", views.password_reset_request, name="password_reset"),
    path("users/profiles/<int:user_id>", views.profile_request, name="profile_request"),
    path("users/profiles/<int:user_id>/image", views.update_profile_image, name="update_profile_image"),
    path("users/create_profile", views.create_profile, name="create_profile"),
    path("users", views.get_all_users, name="users_detail"),
    path("users/user", views.get_current_user, name="users_detail"),
    path("users/<int:user_id>", views.get_only_user, name="user_detail"),
    path("users/roles", views.get_role, name="roles_detail"), 
    path("refresh_token", views.refresh_token, name="refresh_token"),    
    path("test", views.test, name="test"), 

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
