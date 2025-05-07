from rest_framework import serializers
from .models import Localidad, CategoriaObjeto, PerfilUsuario, Objeto, FotoObjeto, SolicitudTransaccion, Valoracion
from django.contrib.auth.models import User

class LocalidadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Localidad
        fields = ['id', 'nombre', 'codigo_postal_base', 'pais', 'activa']
        # También podrías usar fields = '__all__' para incluir todos los campos,
        # pero es mejor ser explícito para la API pública.

class CategoriaObjetoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriaObjeto
        fields = ['id', 'nombre', 'descripcion']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        # Considera si quieres exponer el email públicamente.
        # Podrías tener un UserSerializer más detallado para vistas protegidas
        # y uno más simple para información pública.

class PerfilUsuarioSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True) # Anidado y solo lectura
    localidad_predeterminada_nombre = serializers.CharField(source='localidad_predeterminada.nombre', read_only=True, allow_null=True)

    class Meta:
        model = PerfilUsuario
        fields = ['id', 'user', 'localidad_predeterminada', 'localidad_predeterminada_nombre', 'telefono', 'foto_perfil', 'reputacion']
        # 'localidad_predeterminada' será el ID, 'localidad_predeterminada_nombre' mostrará el nombre.

class FotoObjetoSerializer(serializers.ModelSerializer): # Necesitamos este primero para ObjetoSerializer
    class Meta:
        model = FotoObjeto
        fields = ['id', 'imagen', 'descripcion_foto', 'fecha_subida']

class ObjetoSerializer(serializers.ModelSerializer):
    propietario = UserSerializer(read_only=True)
    # Para campos ForeignKey, por defecto se serializa el ID.
    # Si quieres más detalle, puedes anidar serializers o usar StringRelatedField/SlugRelatedField.
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True, allow_null=True)
    localidad_actual_nombre = serializers.CharField(source='localidad_actual.nombre', read_only=True)
    fotos = FotoObjetoSerializer(many=True, read_only=True) # Para la relación inversa de FotoObjeto

    class Meta:
        model = Objeto
        fields = [
            'id', 'nombre', 'descripcion', 'propietario', 'categoria', 'categoria_nombre',
            'localidad_actual', 'localidad_actual_nombre', 'disponible_para',
            'precio_alquiler_por_dia', 'condiciones_intercambio',
            'fecha_publicacion', 'ultima_modificacion', 'activo', 'fotos'
        ]
        # 'categoria' y 'localidad_actual' serán los IDs.
        # 'categoria_nombre' y 'localidad_actual_nombre' mostrarán los nombres.

class SolicitudTransaccionSerializer(serializers.ModelSerializer):
    objeto = ObjetoSerializer(read_only=True) # Objeto completo, solo lectura en este nivel
    solicitante = UserSerializer(read_only=True)
    # Para la creación, esperaríamos los IDs: objeto_id, solicitante_id
    objeto_id = serializers.PrimaryKeyRelatedField(
        queryset=Objeto.objects.all(), source='objeto', write_only=True
    )
    solicitante_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='solicitante', write_only=True
    )

    # Opcional: si quieres mostrar detalles del objeto ofrecido a cambio
    objeto_ofrecido_intercambio_detalle = ObjetoSerializer(source='objeto_ofrecido_intercambio', read_only=True, allow_null=True)
    objeto_ofrecido_intercambio_id = serializers.PrimaryKeyRelatedField(
        queryset=Objeto.objects.all(), source='objeto_ofrecido_intercambio', write_only=True, allow_null=True, required=False
    )

    class Meta:
        model = SolicitudTransaccion
        fields = [
            'id', 'objeto', 'objeto_id', 'solicitante', 'solicitante_id',
            'tipo_transaccion', 'estado', 'fecha_solicitud',
            'fecha_inicio_deseada', 'fecha_fin_deseada', 'mensaje_solicitud',
            'objeto_ofrecido_intercambio', 'objeto_ofrecido_intercambio_id', 'objeto_ofrecido_intercambio_detalle', # ID y detalle opcional
            'costo_total_acordado', 'fecha_aceptacion_rechazo',
            'fecha_inicio_real', 'fecha_fin_real', 'devuelto_confirmado'
        ]
        read_only_fields = ['fecha_solicitud', 'fecha_aceptacion_rechazo', 'estado'] # Campos que no se deberían establecer directamente al crear/actualizar, o que tienen lógica de negocio

    def create(self, validated_data):
        # Aquí podrías añadir lógica personalizada si es necesario antes de crear la solicitud
        # Por ejemplo, establecer el estado inicial si no se proporciona
        if 'estado' not in validated_data:
            validated_data['estado'] = SolicitudTransaccion.EstadoSolicitud.PENDIENTE
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Lógica personalizada para actualizaciones, por ejemplo, manejo de cambios de estado
        # instance.estado = validated_data.get('estado', instance.estado)
        # ... más lógica ...
        return super().update(instance, validated_data)


class ValoracionSerializer(serializers.ModelSerializer):
    solicitud_detalle = SolicitudTransaccionSerializer(source='solicitud', read_only=True) # Detalle de la solicitud
    usuario_que_valora_detalle = UserSerializer(source='usuario_que_valora', read_only=True)
    usuario_valorado_detalle = UserSerializer(source='usuario_valorado', read_only=True)

    # Para la creación, esperaríamos los IDs
    solicitud_id = serializers.PrimaryKeyRelatedField(
        queryset=SolicitudTransaccion.objects.all(), source='solicitud', write_only=True
    )
    usuario_que_valora_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='usuario_que_valora', write_only=True
    )
    usuario_valorado_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='usuario_valorado', write_only=True
    )

    class Meta:
        model = Valoracion
        fields = [
            'id', 'solicitud', 'solicitud_id', 'solicitud_detalle',
            'usuario_que_valora', 'usuario_que_valora_id', 'usuario_que_valora_detalle',
            'usuario_valorado', 'usuario_valorado_id', 'usuario_valorado_detalle',
            'puntuacion', 'comentario', 'fecha_valoracion'
        ]
        read_only_fields = ['fecha_valoracion']

    def validate(self, data):
        """
        Verifica que el usuario_que_valora y el usuario_valorado sean participantes
        de la solicitud (propietario del objeto o solicitante).
        También verifica que un usuario no se valore a sí mismo.
        Y que la valoración corresponda a una solicitud completada (o en un estado apropiado).
        """
        solicitud = data.get('solicitud') # Esto será la instancia de SolicitudTransaccion gracias a source en el PrimaryKeyRelatedField

        # Si estamos actualizando, la solicitud podría no estar en 'data' si no se cambia.
        # En ese caso, la obtenemos de la instancia del serializer.
        if self.instance:
            solicitud = self.instance.solicitud if solicitud is None else solicitud

        usuario_que_valora = data.get('usuario_que_valora')
        if self.instance and usuario_que_valora is None:
            usuario_que_valora = self.instance.usuario_que_valora

        usuario_valorado = data.get('usuario_valorado')
        if self.instance and usuario_valorado is None:
            usuario_valorado = self.instance.usuario_valorado


        if not solicitud or not usuario_que_valora or not usuario_valorado:
             # Esto no debería ocurrir si los campos son requeridos, pero es una buena verificación.
            raise serializers.ValidationError("Solicitud, usuario que valora y usuario valorado son requeridos.")


        propietario_objeto = solicitud.objeto.propietario
        solicitante_transaccion = solicitud.solicitante

        # Verificar que los usuarios involucrados en la valoración sean el propietario o el solicitante
        if not ( (usuario_que_valora == propietario_objeto and usuario_valorado == solicitante_transaccion) or \
                 (usuario_que_valora == solicitante_transaccion and usuario_valorado == propietario_objeto) ):
            raise serializers.ValidationError(
                "La valoración debe ser entre el propietario del objeto y el solicitante de la transacción."
            )

        if usuario_que_valora == usuario_valorado:
            raise serializers.ValidationError("Un usuario no puede valorarse a sí mismo.")

        # Podrías añadir una validación para asegurar que la solicitud esté en un estado 'COMPLETADA'
        # if solicitud.estado != SolicitudTransaccion.EstadoSolicitud.COMPLETADA:
        #     raise serializers.ValidationError("Solo se pueden valorar transacciones completadas.")

        return data

    def create(self, validated_data):
        # Lógica adicional si es necesario, por ejemplo, actualizar la reputación del usuario_valorado
        valoracion = super().create(validated_data)
        # Ejemplo: (necesitarías una lógica más robusta para calcular la reputación)
        # usuario_valorado = valoracion.usuario_valorado
        # perfil_valorado, created = PerfilUsuario.objects.get_or_create(user=usuario_valorado)
        # # Actualizar reputación (esto es simplista, deberías promediar o sumar)
        # total_puntuacion = sum(v.puntuacion for v in Valoracion.objects.filter(usuario_valorado=usuario_valorado))
        # num_valoraciones = Valoracion.objects.filter(usuario_valorado=usuario_valorado).count()
        # perfil_valorado.reputacion = total_puntuacion / num_valoraciones if num_valoraciones > 0 else 0
        # perfil_valorado.save()
        return valoracion