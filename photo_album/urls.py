from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from albums.views import CustomPasswordResetView, CustomPasswordChangeView, logout_and_redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('albums.urls')),
    path('accounts/password_reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('accounts/password_change/', CustomPasswordChangeView.as_view(), name='password_change'),
    path('accounts/logout/', logout_and_redirect, name='logout'),
    path('accounts/', include('django.contrib.auth.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
