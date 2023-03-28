"""login_with_face URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.urls import path, include, re_path
from django.conf.urls.static import static
from django.conf import settings
from django.views.static import serve
from django.conf import settings
import debug_toolbar


from customuser.api.views import MyTokenObtainPairView

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('recognizer.urls', namespace='recognizer')),
    path('teacher/', include('teacher.urls', namespace='teacher')),
    path("chat/", include("chat.urls", namespace="chat")),
    
    path('api/auth/', include('dj_rest_auth.urls')),
    
    path("api/login-details/", include("login_details.api.urls")),
    path("api/basic/", include("recognizer.api.urls")),
    # path("api//", include("recognizer.api.urls")),
    
    path('api/token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root':settings.MEDIA_ROOT}),
    
    
] 


from django.conf import settings


if settings.DEBUG:
    
    import debug_toolbar
    urlpatterns += [ path('__debug__/', include(debug_toolbar.urls)) ]
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    