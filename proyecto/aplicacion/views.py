from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import viewsets, permissions
from django_filters.rest_framework import DjangoFilterBackend
from .models import (
    Localidad,
    CategoriaObjeto,
    PerfilUsuario,
    Objeto,
    FotoObjeto,
    SolicitudTransaccion,
    Valoracion
)
from .serializers import (
    LocalidadSerializer,
    CategoriaObjetoSerializer,
    UserSerializer, # Aunque no tengamos un UserViewSet aquí, otros serializers lo usan
    PerfilUsuarioSerializer,
    ObjetoSerializer,
    FotoObjetoSerializer,
    SolicitudTransaccionSerializer,
    ValoracionSerializer
)
from django.contrib.auth.models import User

def home(request):
    return HttpResponse("¡Bienvenido a mi aplicación Django!")

def about(request):
    return render(request, 'about.html')

# ViewSets para los modelos

class LocalidadViewSet(viewsets.ModelViewSet):
    queryset = Localidad.objects.all()
    serializer_class = LocalidadSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly] # Ejemplo: cualquiera puede leer, solo autenticados pueden escribir

class CategoriaObjetoViewSet(viewsets.ModelViewSet):
    queryset = CategoriaObjeto.objects.all()
    serializer_class = CategoriaObjetoSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly] # O [permissions.IsAdminUser] si solo admins pueden gestionar categorías

class PerfilUsuarioViewSet(viewsets.ModelViewSet):
    queryset = PerfilUsuario.objects.all()
    serializer_class = PerfilUsuarioSerializer
    permission_classes = [permissions.IsAuthenticated] # Solo usuarios autenticados pueden ver/editar perfiles (podrías necesitar permisos más granulares)

    # Podrías querer filtrar para que un usuario solo vea/edite su propio perfil,
    # o añadir una acción para "mi perfil".
    # def get_queryset(self):
    #     user = self.request.user
    #     if user.is_staff: # Los admins pueden ver todos
    #         return PerfilUsuario.objects.all()
    #     return PerfilUsuario.objects.filter(user=user) # Usuarios normales solo ven el suyo

class ObjetoViewSet(viewsets.ModelViewSet):
    queryset = Objeto.objects.all()
    serializer_class = ObjetoSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['categoria', 'localidad_actual', 'disponible_para']
    permission_classes = [permissions.IsAuthenticatedOrReadOnly] # Cualquiera puede ver, solo autenticados pueden crear/editar

    def perform_create(self, serializer):
        # Asignar el propietario automáticamente al usuario autenticado al crear un objeto
        serializer.save(propietario=self.request.user)

    # Aquí podrías añadir filtros más avanzados (ej. por localidad, categoría, disponibilidad)
    # usando django-filter o implementando el método get_queryset.

class FotoObjetoViewSet(viewsets.ModelViewSet):
    queryset = FotoObjeto.objects.all()
    serializer_class = FotoObjetoSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly] # O permisos más estrictos basados en el propietario del objeto

    # Normalmente, las fotos se gestionan a través del ObjetoViewSet (usando el FotoObjetoSerializer anidado)
    # o con acciones personalizadas. Un ViewSet dedicado podría ser para casos específicos.
    # Podrías querer filtrar por objeto_id si se accede directamente.

class SolicitudTransaccionViewSet(viewsets.ModelViewSet):
    queryset = SolicitudTransaccion.objects.all().select_related('objeto', 'solicitante', 'objeto__propietario')
    serializer_class = SolicitudTransaccionSerializer
    permission_classes = [permissions.IsAuthenticated] # Solo usuarios autenticados pueden interactuar con solicitudes

    def get_queryset(self):
        user = self.request.user
        # Un usuario debería poder ver las solicitudes que ha hecho o las solicitudes para sus objetos
        return SolicitudTransaccion.objects.filter(
            models.Q(solicitante=user) | models.Q(objeto__propietario=user)
        ).distinct()

    def perform_create(self, serializer):
        # Asignar el solicitante automáticamente al usuario autenticado
        serializer.save(solicitante=self.request.user)

    # Aquí podrías añadir acciones personalizadas como "aceptar_solicitud", "rechazar_solicitud", etc.
    # @action(detail=True, methods=['post'])
    # def aceptar(self, request, pk=None):
    #     solicitud = self.get_object()
    #     # Lógica para aceptar...
    #     solicitud.estado = SolicitudTransaccion.EstadoSolicitud.ACEPTADA
    #     solicitud.save()
    #     return Response({'status': 'solicitud aceptada'})

class ValoracionViewSet(viewsets.ModelViewSet):
    queryset = Valoracion.objects.all().select_related('solicitud', 'usuario_que_valora', 'usuario_valorado')
    serializer_class = ValoracionSerializer
    permission_classes = [permissions.IsAuthenticated] # Solo usuarios autenticados pueden crear/ver valoraciones

    def get_queryset(self):
        user = self.request.user
        # Un usuario puede ver las valoraciones que ha emitido o recibido
        return Valoracion.objects.filter(
            models.Q(usuario_que_valora=user) | models.Q(usuario_valorado=user)
        ).distinct()

    def perform_create(self, serializer):
        # Asignar el usuario_que_valora automáticamente al usuario autenticado
        serializer.save(usuario_que_valora=self.request.user)

# No creamos un UserViewSet aquí porque DRF no lo proporciona por defecto de forma segura
# para la creación/gestión de usuarios (especialmente contraseñas).
# La creación de usuarios se suele manejar con librerías como djoser o django-rest-auth,
# o con una vista personalizada si necesitas algo simple.
# Para listar/recuperar usuarios (si es necesario y seguro), podrías crear un ReadOnlyModelViewSet.