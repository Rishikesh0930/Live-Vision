"""
URL configuration for LVProject project.

The `urlpatterns` list routes URLs to  For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from App.views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', start, name='start-page'),
    path('signup/', signupPage, name='signup-page'),
    path('login/', loginPage, name='login-page'),
    path('home/', home, name='home-page'),
    path('livestream/', live_stream, name='live-stream'),
    path('about/', about, name='about-page'),
    path('videos/', video, name='video-page'),
    path('help/', help, name='help-page'),
    path("video_feed/", video_feed, name="video_feed"),
    path("start_stream/", start_stream, name="start_stream"),
    path("stop_stream/", stop_stream, name="stop_stream"),
    path('delete_video/<int:video_id>/', delete_video, name='delete_video'),
    path("get-object-details/", get_object_details, name="get-object-details"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
