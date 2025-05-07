from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views # Importa tus vistas (donde están los ViewSets)

# Crea un router y registra nuestros viewsets con él.
router = DefaultRouter()
router.register(r'localidades', views.LocalidadViewSet, basename='localidad')
router.register(r'categorias', views.CategoriaObjetoViewSet, basename='categoriaobjeto')
router.register(r'perfiles', views.PerfilUsuarioViewSet, basename='perfilusuario')
router.register(r'objetos', views.ObjetoViewSet, basename='objeto')
router.register(r'fotos', views.FotoObjetoViewSet, basename='fotoobjeto') # Considera si este es necesario o se maneja anidado
router.register(r'solicitudes', views.SolicitudTransaccionViewSet, basename='solicitudtransaccion')
router.register(r'valoraciones', views.ValoracionViewSet, basename='valoracion')

# Las URLs de la API son determinadas automáticamente por el router.
# También podemos añadir URLs para vistas basadas en funciones o clases que no sean ViewSets.
urlpatterns = [
    path('', include(router.urls)),
    # Aquí podrías añadir otras URLs específicas de la API de tu aplicación si las necesitas
    # path('mi-vista-personalizada/', views.mi_vista_api_personalizada, name='mi-vista-api'),
]