from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from aplicacion import views as aplicacion_views

from rest_framework_simplejwt.views import (  # Importar vistas de simplejwt
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,  # Opcional, para verificar un token
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', aplicacion_views.home, name='home'),
    path('about/', aplicacion_views.about, name='about'),
    path('api/', include('aplicacion.urls')),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    # URLs para JWT
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # Para obtener tokens
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # Para refrescar tokens
    # path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),  # Opcional: para verificar un token
]

if settings.DEBUG:  # Solo para desarrollo
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)  # Si tienes STATIC_ROOT definido