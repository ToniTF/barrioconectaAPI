from django.contrib import admin
from .models import (
    Localidad,
    PerfilUsuario,
    CategoriaObjeto,
    Objeto,
    FotoObjeto,
    SolicitudTransaccion,
    Valoracion
)

# Registros básicos
admin.site.register(Localidad)
admin.site.register(CategoriaObjeto)
admin.site.register(FotoObjeto) # Puede que quieras un inline para Objeto más adelante
admin.site.register(Valoracion)

# Personalizaciones (opcional, pero recomendado para mejor usabilidad)

@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ('user', 'localidad_predeterminada', 'reputacion')
    search_fields = ('user__username', 'user__email', 'telefono')
    list_filter = ('localidad_predeterminada',)

class FotoObjetoInline(admin.TabularInline): # o admin.StackedInline
    model = FotoObjeto
    extra = 1 # Número de formularios extra para fotos

@admin.register(Objeto)
class ObjetoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'propietario', 'categoria', 'localidad_actual', 'disponible_para', 'activo', 'fecha_publicacion')
    search_fields = ('nombre', 'descripcion', 'propietario__username')
    list_filter = ('activo', 'disponible_para', 'categoria', 'localidad_actual', 'fecha_publicacion')
    date_hierarchy = 'fecha_publicacion'
    inlines = [FotoObjetoInline] # Para añadir/editar fotos directamente desde el objeto

@admin.register(SolicitudTransaccion)
class SolicitudTransaccionAdmin(admin.ModelAdmin):
    list_display = ('objeto', 'solicitante', 'tipo_transaccion', 'estado', 'fecha_solicitud')
    search_fields = ('objeto__nombre', 'solicitante__username')
    list_filter = ('tipo_transaccion', 'estado', 'fecha_solicitud')
    date_hierarchy = 'fecha_solicitud'
    # Podrías añadir campos readonly o personalizar el form si es necesario