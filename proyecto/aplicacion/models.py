from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _ # Para cadenas traducibles

class Localidad(models.Model):
    nombre = models.CharField(max_length=100, unique=True, verbose_name=_("Nombre de la localidad"))
    codigo_postal_base = models.CharField(max_length=10, blank=True, null=True, verbose_name=_("Código Postal Base"))
    pais = models.CharField(max_length=50, default="España", verbose_name=_("País"))
    activa = models.BooleanField(default=True, verbose_name=_("Activa"))

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = _("Localidad")
        verbose_name_plural = _("Localidades")
        ordering = ['nombre']

class PerfilUsuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil', verbose_name=_("Usuario"))
    localidad_predeterminada = models.ForeignKey(Localidad, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Localidad Predeterminada"))
    telefono = models.CharField(max_length=20, blank=True, null=True, verbose_name=_("Teléfono"))
    foto_perfil = models.ImageField(upload_to='fotos_perfil/', null=True, blank=True, verbose_name=_("Foto de Perfil"))
    reputacion = models.FloatField(default=0.0, verbose_name=_("Reputación")) # Podría calcularse o ser un promedio de valoraciones

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = _("Perfil de Usuario")
        verbose_name_plural = _("Perfiles de Usuario")

class CategoriaObjeto(models.Model):
    nombre = models.CharField(max_length=100, unique=True, verbose_name=_("Nombre de la categoría"))
    descripcion = models.TextField(blank=True, null=True, verbose_name=_("Descripción"))
    # icono = models.CharField(max_length=50, blank=True, null=True) # Podrías añadir un campo para un icono (ej. FontAwesome class)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = _("Categoría de Objeto")
        verbose_name_plural = _("Categorías de Objetos")
        ordering = ['nombre']

class Objeto(models.Model):
    class TipoDisponibilidad(models.TextChoices):
        PRESTAMO = 'PR', _('Préstamo')
        ALQUILER = 'AL', _('Alquiler')
        INTERCAMBIO = 'IN', _('Intercambio')
        PRESTAMO_ALQUILER = 'PA', _('Préstamo o Alquiler')
        TODOS = 'TO', _('Préstamo, Alquiler o Intercambio')

    nombre = models.CharField(max_length=200, verbose_name=_("Nombre del objeto"))
    descripcion = models.TextField(verbose_name=_("Descripción"))
    propietario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='objetos_poseidos', verbose_name=_("Propietario"))
    categoria = models.ForeignKey(CategoriaObjeto, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Categoría"))
    localidad_actual = models.ForeignKey(Localidad, on_delete=models.PROTECT, verbose_name=_("Localidad Actual del Objeto")) # Proteger para no borrar localidad si tiene objetos
    disponible_para = models.CharField(
        max_length=2,
        choices=TipoDisponibilidad.choices,
        default=TipoDisponibilidad.PRESTAMO,
        verbose_name=_("Disponible para")
    )
    precio_alquiler_por_dia = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name=_("Precio Alquiler por Día (€)"))
    condiciones_intercambio = models.TextField(blank=True, null=True, verbose_name=_("Condiciones para Intercambio"))
    fecha_publicacion = models.DateTimeField(auto_now_add=True, verbose_name=_("Fecha de Publicación"))
    ultima_modificacion = models.DateTimeField(auto_now=True, verbose_name=_("Última Modificación"))
    activo = models.BooleanField(default=True, verbose_name=_("Activo/Disponible")) # Si el objeto está listado y disponible en general
    # Podríamos añadir un campo de estado más granular, ej: 'disponible', 'prestado', 'en_alquiler_activo'

    def __str__(self):
        return f"{self.nombre} ({self.propietario.username})"

    class Meta:
        verbose_name = _("Objeto")
        verbose_name_plural = _("Objetos")
        ordering = ['-fecha_publicacion']

class FotoObjeto(models.Model):
    objeto = models.ForeignKey(Objeto, related_name='fotos', on_delete=models.CASCADE, verbose_name=_("Objeto"))
    imagen = models.ImageField(upload_to='fotos_objetos/', verbose_name=_("Imagen"))
    descripcion_foto = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Descripción de la Foto"))
    fecha_subida = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Foto de {self.objeto.nombre} ({self.id})"

    class Meta:
        verbose_name = _("Foto de Objeto")
        verbose_name_plural = _("Fotos de Objetos")
        ordering = ['fecha_subida']

# --- Modelos para Transacciones (Borrador inicial) ---
class SolicitudTransaccion(models.Model):
    class TipoTransaccion(models.TextChoices):
        PRESTAMO = 'PR', _('Préstamo')
        ALQUILER = 'AL', _('Alquiler')
        INTERCAMBIO = 'IN', _('Intercambio')

    class EstadoSolicitud(models.TextChoices):
        PENDIENTE = 'PE', _('Pendiente')
        ACEPTADA = 'AC', _('Aceptada')
        RECHAZADA = 'RE', _('Rechazada')
        CANCELADA_SOLICITANTE = 'CS', _('Cancelada por Solicitante')
        CANCELADA_PROPIETARIO = 'CP', _('Cancelada por Propietario')
        EN_CURSO = 'EC', _('En Curso') # Para alquileres/préstamos activos
        COMPLETADA = 'CO', _('Completada')
        DISPUTA = 'DI', _('En Disputa')

    objeto = models.ForeignKey(Objeto, on_delete=models.CASCADE, related_name='solicitudes', verbose_name=_("Objeto Solicitado"))
    solicitante = models.ForeignKey(User, on_delete=models.CASCADE, related_name='solicitudes_realizadas', verbose_name=_("Solicitante"))
    # propietario_objeto se puede obtener de objeto.propietario
    tipo_transaccion = models.CharField(max_length=2, choices=TipoTransaccion.choices, verbose_name=_("Tipo de Transacción"))
    estado = models.CharField(max_length=2, choices=EstadoSolicitud.choices, default=EstadoSolicitud.PENDIENTE, verbose_name=_("Estado"))

    fecha_solicitud = models.DateTimeField(auto_now_add=True, verbose_name=_("Fecha de Solicitud"))
    fecha_inicio_deseada = models.DateField(null=True, blank=True, verbose_name=_("Fecha Inicio Deseada")) # Para alquiler/préstamo
    fecha_fin_deseada = models.DateField(null=True, blank=True, verbose_name=_("Fecha Fin Deseada"))     # Para alquiler/préstamo
    mensaje_solicitud = models.TextField(blank=True, null=True, verbose_name=_("Mensaje para el Propietario"))

    # Para intercambios
    objeto_ofrecido_intercambio = models.ForeignKey(Objeto, on_delete=models.SET_NULL, null=True, blank=True, related_name='solicitudes_donde_se_ofrece', verbose_name=_("Objeto Ofrecido a Cambio"))

    # Para alquileres
    costo_total_acordado = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name=_("Costo Total Acordado (€)"))

    # Seguimiento
    fecha_aceptacion_rechazo = models.DateTimeField(null=True, blank=True, verbose_name=_("Fecha Aceptación/Rechazo"))
    fecha_inicio_real = models.DateTimeField(null=True, blank=True, verbose_name=_("Fecha Inicio Real"))
    fecha_fin_real = models.DateTimeField(null=True, blank=True, verbose_name=_("Fecha Fin Real"))
    devuelto_confirmado = models.BooleanField(default=False, verbose_name=_("Devolución Confirmada")) # Para préstamos/alquileres

    def __str__(self):
        return f"Solicitud de {self.solicitante.username} para {self.objeto.nombre} ({self.get_tipo_transaccion_display()})"

    class Meta:
        verbose_name = _("Solicitud de Transacción")
        verbose_name_plural = _("Solicitudes de Transacciones")
        ordering = ['-fecha_solicitud']

class Valoracion(models.Model):
    solicitud = models.ForeignKey(SolicitudTransaccion, on_delete=models.CASCADE, related_name='valoraciones', verbose_name=_("Transacción Valorada"))
    # Se puede valorar al solicitante o al propietario
    usuario_que_valora = models.ForeignKey(User, on_delete=models.CASCADE, related_name='valoraciones_emitidas', verbose_name=_("Usuario que Valora"))
    usuario_valorado = models.ForeignKey(User, on_delete=models.CASCADE, related_name='valoraciones_recibidas', verbose_name=_("Usuario Valorado"))
    puntuacion = models.PositiveSmallIntegerField(choices=[(i, str(i)) for i in range(1, 6)], verbose_name=_("Puntuación (1-5)")) # 1 a 5 estrellas
    comentario = models.TextField(blank=True, null=True, verbose_name=_("Comentario"))
    fecha_valoracion = models.DateTimeField(auto_now_add=True, verbose_name=_("Fecha de Valoración"))

    def __str__(self):
        return f"Valoración de {self.usuario_que_valora.username} a {self.usuario_valorado.username} ({self.puntuacion} estrellas)"

    class Meta:
        verbose_name = _("Valoración")
        verbose_name_plural = _("Valoraciones")
        ordering = ['-fecha_valoracion']
        unique_together = [['solicitud', 'usuario_que_valora', 'usuario_valorado']] # Evitar múltiples valoraciones de la misma persona a otra por la misma transacción