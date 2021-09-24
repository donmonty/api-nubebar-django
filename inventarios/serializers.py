from django.contrib.auth import get_user_model
from rest_framework import serializers
from core import models
import datetime
import re
from django.utils.timezone import make_aware


class ItemInspeccionPostSerializer(serializers.ModelSerializer):
    """ Serializador para crear los ItemInspeccion de una Inspeccion """

    #botella = serializers.PrimaryKeyRelatedField(read_only=False, queryset=models.Botella.objects.all())
    botella = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = models.ItemInspeccion
        fields = ('botella', 'peso_botella')
        #exclude = ('inspeccion',)


class InspeccionPostSerializer(serializers.ModelSerializer):
    """ Crea una Inspeccion """

    #items_inspeccionados = ItemInspeccionPostSerializer(many=True)
    #items_inspeccionados = ItemInspeccionPostSerializer(many=True, read_only=True)
    almacen = serializers.PrimaryKeyRelatedField(read_only=False, queryset=models.Almacen.objects.all())
    sucursal = serializers.PrimaryKeyRelatedField(read_only=False, queryset=models.Sucursal.objects.all())
    #usuario_alta = serializers.PrimaryKeyRelatedField(read_only=False, queryset=get_user_model().objects.all())

    class Meta:
        model = models.Inspeccion
        fields = (
            'id',
            'almacen',
            'sucursal',
            #'usuario_alta',
            'fecha_alta',
            'timestamp_alta',
            'estado',
            #'items_inspeccionados'
        )

    def create(self, validated_data):

        """
        :::: IMPORTANTE ::::
        Antes que nada checamos que haya botellas para inpseccionar. Esto
        significa que SI hubo consumo de alcohol.
        Si no hubo consumo, no hay botellas para inspeccionar y no hacemos ninguna
        inspección, sin importar cualquier cosa.
        """
        botellas = self.context['lista_botellas_inspeccionar']
        if botellas is not None:

            """
            Si existe una inspección previa registrada
            """
            # Checamos si existe una inspección previa registrada
            if self.context['fecha_ultima_inspeccion'] is not None:
                # Tomamos la información extra del contexto
                fecha_hoy = datetime.date.today()
                #print('::: FECHA DE HOY ::::')
                #print(fecha_hoy)
                estado_ultima_inspeccion = self.context['estado_ultima_inspeccion']
                fecha_ultima_inspeccion = self.context['fecha_ultima_inspeccion']
                botellas = self.context['lista_botellas_inspeccionar']
                #usuario = self.context['usuario']
                #print('::: ESTADO INSPECCION ANTERIOR :::')
                #print(estado_ultima_inspeccion)
                #print('::: FECHA INSPECCION ANTERIOR :::')
                #print(fecha_ultima_inspeccion)
                #print('::: FECHA HOY > FECHA ANTERIOR? :::')
                #print(fecha_hoy > fecha_ultima_inspeccion)
                #print('::: USUARIO INSPECCION PREVIA :::')
                #print(usuario)
                #print('::: LISTA DE BOTELLAS :::')
                #print(botellas)

                """
                SI la inspección previa está cerrada y la fecha de hoy es mayor que 
                que la fecha de ésta, creamos una nueva inspección.
                """
                if (estado_ultima_inspeccion == '1') and (fecha_hoy > fecha_ultima_inspeccion):
                    #inspeccion = models.Inspeccion.objects.create(usuario_alta=usuario, **validated_data)
                    inspeccion = models.Inspeccion.objects.create(**validated_data)
                    #print('::: CREAMOS UNA INSPECCION :::')
                    #print(inspeccion)

                    #print('::: LISTA DE BOTELLAS :::')
                    #print(botellas)

                    # Creamos los ItemInspeccion
                    for botella in botellas:
                        # Tomamos el id de la botella
                        botella_id = botella.id
                        # Creamos el ItemInspeccion
                        ii = models.ItemInspeccion.objects.create(inspeccion=inspeccion, botella=botella)
                        #print('::: ITEM INSPECCION :::')
                        #print(ii)

                    #print(inspeccion.items_inspeccionados.all())
                    #print(inspeccion.items_inspeccionados.count())

                    return inspeccion

                # Si la fecha de hoy es igual o menor que la de la inspección previa, marcar error
                elif estado_ultima_inspeccion == '1' and fecha_hoy <= fecha_ultima_inspeccion:
                    raise serializers.ValidationError('Solo es posible realizar una inspección al día.')

                # Si la inspección previa está abierta, marcar error
                elif estado_ultima_inspeccion == '0':
                    raise serializers.ValidationError('No es posible hacer una nueva inspección si la anterior no se ha cerrado')

            """
            SI no hay inspecciones registradas, creamos una nueva inspección
            (creamos la primera inspección ever)
            """
        
            inspeccion = models.Inspeccion.objects.create(**validated_data)
            #print('::: NO HAY INSPECCIONES REGISTRADAS :::')
            #print(inspeccion)
            # Tomamos la información extra del contexto
            botellas = self.context['lista_botellas_inspeccionar']
            #usuario = self.context['usuario']

            #print('::: LISTA DE BOTELLAS (no hay inspecciones previas) :::')
            #print(botellas)


            # Creamos los ItemInspeccion
            for botella in botellas:
                botella_id = botella.id
                models.ItemInspeccion.objects.create(inspeccion=inspeccion, botella=botella)

            return inspeccion

        """
        Si no hay botellas que inspeccionar, NO hacemos ninguna inspección
        """
        #print('::: NO HAY BOTELLAS QUE INSPECCIONAR :::')
        raise serializers.ValidationError('No se puede crear una nueva inspección porque no hubo consumo de alcohol.')



#-----------------------------------------------------------------

class InspeccionListSerializer(serializers.ModelSerializer):
    """ 
    Arroja la lista de Inspecciones de un almacén
    """
    class Meta:
        model = models.Inspeccion
        fields = (
            'id',
            'almacen',
            'sucursal',
            'fecha_alta',
            'estado'
        )


class BotellaDetalleSerializer(serializers.ModelSerializer):
    """ Detalle de Botella """

    class Meta:
        model = models.Botella
        fields = '__all__'
        depth = 1
        # fields = (
        #     'folio',
        #     'estado',
        #     'ingrediente',
        #     'categoria'
        # )


class ItemInspeccionDetalleSerializer(serializers.ModelSerializer):
    """ Detalle de ItemInspeccion """

    botella = BotellaDetalleSerializer()

    class Meta:
        model = models.ItemInspeccion
        fields = ('id', 'botella', 'peso_botella', 'inspeccionado')

#------------------------------------------------------------------


class InspeccionDetalleSerializer(serializers.ModelSerializer):
    """ Arroja una Inspeccion con el detalle de sus ItemInspeccion """

    items_inspeccionados = ItemInspeccionDetalleSerializer(many=True)

    class Meta:
        model = models.Inspeccion
        fields = (
            'id',
            'almacen',
            'sucursal',
            'estado',
            'fecha_alta',
            'usuario_alta',
            'items_inspeccionados'
        )

#------------------------------------------------------------------
class ItemInspeccionSerializer(serializers.ModelSerializer):
    """ Despliega el detalle de un ItemInspeccion """

    class Meta:
        model = models.ItemInspeccion
        fields = ('id', 'peso_botella', 'timestamp_inspeccion')



class BotellaItemInspeccionSerializer(serializers.ModelSerializer):
    """ Despliega una botella con su lista de ItemsInspeccion """

    inspecciones_botella = ItemInspeccionSerializer(many=True)

    class Meta:
        model = models.Botella
        fields = (
            'folio',
            'ingrediente',
            'categoria',
            'peso_inicial',
            'peso_actual',
            'precio_unitario',
            'proveedor',
            'fecha_registro',
            'inspecciones_botella'
        )

#------------------------------------------------------------------
class AlmacenSerializer(serializers.ModelSerializer):
    """ Despliega un Almacen """
     
    class Meta:
        model = models.Almacen
        fields = (
            'id',
            'nombre',
            'numero',
        )

#------------------------------------------------------------------
class SucursalSerializer(serializers.ModelSerializer):
    """ Despliega una sucursal, excepto el CLiente """

    almacenes = AlmacenSerializer(read_only=True, many=True)

    class Meta:
        model = models.Sucursal
        fields = (
            'id',
            'nombre',
            'razon_social',
            'rfc',
            'direccion',
            'ciudad',
            'latitud',
            'longitud',
            'codigo_postal',
            'slug',
            'almacenes'
        )

#------------------------------------------------------------------
class SucursalDetalleSerializer(serializers.ModelSerializer):
    """ Despliega una sucursal con sus sucursales asociadas """

    almacenes = AlmacenSerializer(many=True)

    class Meta:
        model = models.Sucursal
        fields = (
            'id',
            'nombre',
            'razon_social',
            'rfc',
            'direccion',
            'ciudad',
            'latitud',
            'longitud',
            'codigo_postal',
            'slug',
            'almacenes',
        )

    # class Meta:
    #     model = models.Sucursal
    #     fields = '__all__'
    #     depth = 1

#------------------------------------------------------------------
class ItemInspeccionUpdateSerializer(serializers.ModelSerializer):
    """ Actualiza el peso_botella y el status de un ItemInspeccion """

    class Meta:
        model = models.ItemInspeccion
        fields = ('id', 'peso_botella', 'timestamp_inspeccion', 'inspeccionado')

   


#------------------------------------------------------------------
class InspeccionUpdateSerializer(serializers.ModelSerializer):

    usuario_cierre = serializers.PrimaryKeyRelatedField(read_only=False, queryset=get_user_model().objects.all())

    class Meta:
        model = models.Inspeccion
        fields = (
            'id',
            'almacen',
            'sucursal',
            'estado',
            'fecha_alta',
            'usuario_alta',
            'usuario_cierre',
            'fecha_update',
            'timestamp_update',
        )

#------------------------------------------------------------------
class BotellaUpdateEstadoSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Botella
        fields = (
            'folio',
            'ingrediente',
            'categoria',
            'peso_inicial',
            'peso_actual',
            'precio_unitario',
            'proveedor',
            'fecha_registro',
            'fecha_baja',
            'estado',
        )


class ItemInspeccionBotellaUpdateSerializer(serializers.ModelSerializer):

    botella = BotellaUpdateEstadoSerializer()

    class Meta:
        model = models.ItemInspeccion
        fields = (
            'id',
            'botella',
            'peso_botella',
            'timestamp_inspeccion',
            'inspeccionado'
        )

    def update(self, instance, validated_data):
        # Tomamos los datos validados para actualizar nuestra Botella
        data_botella = validated_data.pop('botella')
        # Actualizamos los datos de nuestro ItemInspeccion
        instance.peso_botella = validated_data.get('peso_botella', instance.peso_botella)
        instance.inspeccionado = True
        # Actualizamos la instancia de nuestra Botella (estado y peso y 'peso_actual')
        botella = instance.botella
        botella.estado = data_botella['estado']
        botella.peso_actual = validated_data.get('peso_botella', None)

        # Si el estado de la botella es 'VACIA', asignamos la fecha de baja:
        if data_botella['estado'] == '0':
            # Asignamos la fecha de baja a la botella, evitando asignar un naive datetime
            naive_datetime = datetime.datetime.now()
            aware_datetime = make_aware(naive_datetime)
            botella.fecha_baja = aware_datetime 
        #instance.botella.estado = data_botella['estado']

        # Guardamos los cambios en nuestras instancias de Botella e ItemInspeccion
        botella.save()
        instance.save()
        return instance



class ItemInspeccionUpdateSerializer2(serializers.ModelSerializer):
    """ Actualiza el peso_botella y el status de un ItemInspeccion y su Botella asociada """

    botella = BotellaUpdateEstadoSerializer()

    class Meta:
        model = models.ItemInspeccion
        fields = ('id', 'peso_botella', 'timestamp_inspeccion', 'inspeccionado', 'botella')
        depth = 1

    def update(self, instance, validated_data):
        # Tomamos los datos validados para actualizar nuestra Botella
        data_botella = validated_data.pop('botella')
        # Actualizamos los datos de nuestro ItemInspeccion
        instance.peso_botella = validated_data.get('peso_botella', instance.peso_botella)
        instance.inspeccionado = True
        # Actualizamos la instancia de nuestra Botella (estado y peso)
        botella = instance.botella
        botella.estado = data_botella['estado']
        botella.peso_actual = validated_data.get('peso_botella', None)



        #instance.botella.estado = data_botella['estado']

        # Guardamos los cambios en nuestras instancias de Botella e ItemInspeccion
        botella.save()
        instance.save()
        return instance


#------------------------------------------------------------------
class IngredienteSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Ingrediente
        fields = (
            'id',
            'codigo',
            'nombre',
            'categoria',
            'factor_peso'
        )


class ProductoIngredienteSerializer(serializers.ModelSerializer):

    ingrediente = IngredienteSerializer()

    class Meta:
        model = models.Producto
        # fields = (
        #     'id',
        #     'folio',
        #     'ingrediente',
        #     'peso_cristal',
        #     'precio_unitario',
        #     'fecha_registro'
        # )
        fields = '__all__'
        depth = 1

#------------------------------------------------------------------
class CategoriaSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Categoria
        fields = ('id', 'nombre',)

#------------------------------------------------------------------
class IngredienteCategoriaSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Ingrediente
        fields = (
            'id',
            'codigo',
            'nombre',
            #'categoria',
            #'factor_peso'
        )

class CategoriaIngredientesSerializer(serializers.ModelSerializer):

    ingredientes = IngredienteCategoriaSerializer(many=True)

    class Meta:
        model = models.Categoria
        fields = (
            'id',
            'nombre',
            'ingredientes'
        )

#------------------------------------------------------------------
"""
-----------------------------------------------------------------------
Serializador para crear botellas nacionales
-----------------------------------------------------------------------
"""
class BotellaPostSerializer(serializers.ModelSerializer):

    almacen = serializers.PrimaryKeyRelatedField(read_only=False, queryset=models.Almacen.objects.all())
    sucursal = serializers.PrimaryKeyRelatedField(read_only=False, queryset=models.Sucursal.objects.all())
    usuario_alta = serializers.PrimaryKeyRelatedField(read_only=False, queryset=get_user_model().objects.all())
    producto = serializers.PrimaryKeyRelatedField(read_only=False, queryset=models.Producto.objects.all())
    proveedor = serializers.PrimaryKeyRelatedField(read_only=False, queryset=models.Proveedor.objects.all())

    class Meta:
        model = models.Botella
        fields = (
            'id',
            # Datos del marbete
            'folio',
            'tipo_marbete',
            'fecha_elaboracion_marbete',
            'lote_produccion_marbete',
            'url',
            'producto',
            # Datos del producto en el marbete
            'nombre_marca',
            'tipo_producto',
            'graduacion_alcoholica',
            'capacidad',
            'origen_del_producto',
            'fecha_envasado',
            'lote_produccion',
            'nombre_fabricante',
            'rfc_fabricante',
            # Datos registrados con app móvil:
            'estado',
            'fecha_registro',
            'fecha_baja',
            'usuario_alta',
            'sucursal',
            'almacen',
            'peso_cristal',
            'peso_inicial',
            'peso_actual',
            'precio_unitario',
            'proveedor',
            'ingrediente',
            'categoria'
        )


    def validate_peso(self, value):
        """ Validamos que el campo de 'peso_inicial' no esté vacío """

        if value is None:
            raise serializers.ValidationError("Para guardar la botella primero hay que pesarla.")
        
        return value 


    def create(self, validated_data):

        # Tomamos las variables del Producto que se asignarán a la Botella
        #producto_id = validated_data.get('producto')
        producto_asignado = validated_data.get('producto')
        producto_id = producto_asignado.id
        #print('::: ID PRODUCTO :::')
        #print(producto_id)
        #producto_asignado = models.Producto.objects.get(id=producto_id)
        

        peso_cristal = producto_asignado.peso_cristal
        precio_unitario = producto_asignado.precio_unitario
        capacidad = producto_asignado.capacidad
        #proveedor = producto_asignado.proveedor

        # Creamos la botella
        botella = models.Botella.objects.create(
            folio=validated_data.get('folio'),
            tipo_marbete=validated_data.get('tipo_marbete'),
            fecha_elaboracion_marbete=validated_data.get('fecha_elaboracion_marbete'),
            lote_produccion_marbete=validated_data.get('lote_produccion_marbete'),
            url=validated_data.get('url'),
            producto=producto_asignado,
            #producto=producto_asignado.id,
            #producto=validated_data.get('producto'),
            # Datos del producto en marbete
            nombre_marca=validated_data.get('nombre_marca'),
            tipo_producto=validated_data.get('tipo_producto'),
            graduacion_alcoholica=validated_data.get('graduacion_alcoholica'),
            #capacidad=validated_data.get('capacidad'),
            capacidad=capacidad, # Tomamos la capacidad directamente del Producto porque a veces la info del marbete es erronea
            origen_del_producto=validated_data.get('origen_del_producto'),
            fecha_envasado=validated_data.get('fecha_envasado'),
            lote_produccion=validated_data.get('lote_produccion'),
            nombre_fabricante=validated_data.get('nombre_fabricante'),
            rfc_fabricante=validated_data.get('rfc_fabricante'),
            # Datos registrados con app movil
            usuario_alta=validated_data.get('usuario_alta'),
            sucursal=validated_data.get('sucursal'),
            almacen=validated_data.get('almacen'),
            peso_cristal=peso_cristal,
            precio_unitario=precio_unitario,
            proveedor=validated_data.get('proveedor'),
            # Datos obtenidos de la báscula
            peso_inicial=validated_data.get('peso_inicial'),
            peso_actual=validated_data.get('peso_inicial')

        )

        return botella


#------------------------------------------------------------------
"""
-----------------------------------------------------------------------
Serializador para crear botellas importadas
-----------------------------------------------------------------------
"""
class BotellaImportadaPostSerializer(serializers.ModelSerializer):

    almacen = serializers.PrimaryKeyRelatedField(read_only=False, queryset=models.Almacen.objects.all())
    sucursal = serializers.PrimaryKeyRelatedField(read_only=False, queryset=models.Sucursal.objects.all())
    usuario_alta = serializers.PrimaryKeyRelatedField(read_only=False, queryset=get_user_model().objects.all())
    producto = serializers.PrimaryKeyRelatedField(read_only=False, queryset=models.Producto.objects.all())
    proveedor = serializers.PrimaryKeyRelatedField(read_only=False, queryset=models.Proveedor.objects.all())

    class Meta:
        model = models.Botella
        fields = (
            'id',
            # Datos del marbete
            'folio',
            'tipo_marbete',
            'fecha_elaboracion_marbete',
            'lote_produccion_marbete',
            'url',
            'producto',
            # Datos del producto en el marbete
            'nombre_marca',
            'tipo_producto',
            'graduacion_alcoholica',
            'capacidad',
            'origen_del_producto',
            'fecha_importacion',
            'numero_pedimento',
            'nombre_fabricante',
            'rfc_fabricante',
            # Datos registrados con app móvil:
            'estado',
            'fecha_registro',
            'fecha_baja',
            'usuario_alta',
            'sucursal',
            'almacen',
            'peso_cristal',
            'peso_inicial',
            'peso_actual',
            'precio_unitario',
            'proveedor',
            'ingrediente',
            'categoria'
        )


    def validate_peso(self, value):
        """ Validamos que el campo de 'peso_inicial' no esté vacío """

        if value is None:
            raise serializers.ValidationError("Para guardar la botella primero hay que pesarla.")
        
        return value 


    def create(self, validated_data):

        # Tomamos las variables del Producto que se asignarán a la Botella
        #producto_id = validated_data.get('producto')
        producto_asignado = validated_data.get('producto')
        producto_id = producto_asignado.id
        #print('::: ID PRODUCTO :::')
        #print(producto_id)
        #producto_asignado = models.Producto.objects.get(id=producto_id)
        

        peso_cristal = producto_asignado.peso_cristal
        precio_unitario = producto_asignado.precio_unitario
        capacidad = producto_asignado.capacidad
        #proveedor = producto_asignado.proveedor

        # Creamos la botella
        botella = models.Botella.objects.create(
            folio=validated_data.get('folio'),
            tipo_marbete=validated_data.get('tipo_marbete'),
            fecha_elaboracion_marbete=validated_data.get('fecha_elaboracion_marbete'),
            lote_produccion_marbete=validated_data.get('lote_produccion_marbete'),
            url=validated_data.get('url'),
            producto=producto_asignado,
            #producto=producto_asignado.id,
            #producto=validated_data.get('producto'),
            # Datos del producto en marbete
            nombre_marca=validated_data.get('nombre_marca'),
            tipo_producto=validated_data.get('tipo_producto'),
            graduacion_alcoholica=validated_data.get('graduacion_alcoholica'),
            #capacidad=validated_data.get('capacidad'),
            capacidad=capacidad, # Tomamos la capacidad directamente del Producto porque a veces la info del marbete es erronea
            origen_del_producto=validated_data.get('origen_del_producto'),
            fecha_importacion=validated_data.get('fecha_importacion'),
            numero_pedimento=validated_data.get('numero_pedimento'),
            nombre_fabricante=validated_data.get('nombre_fabricante'),
            rfc_fabricante=validated_data.get('rfc_fabricante'),
            # Datos registrados con app movil
            usuario_alta=validated_data.get('usuario_alta'),
            sucursal=validated_data.get('sucursal'),
            almacen=validated_data.get('almacen'),
            peso_cristal=peso_cristal,
            precio_unitario=precio_unitario,
            proveedor=validated_data.get('proveedor'),
            # Datos obtenidos de la báscula
            peso_inicial=validated_data.get('peso_inicial'),
            peso_actual=validated_data.get('peso_inicial')

        )

        return botella


#------------------------------------------------------------------
class ProductoWriteSerializer(serializers.ModelSerializer):

    ingrediente = serializers.PrimaryKeyRelatedField(read_only=False, queryset=models.Ingrediente.objects.all())

    class Meta:
        model = models.Producto
        fields = (
            'id',
            # Datos del marbete
            'folio',
            'tipo_marbete',
            'fecha_elaboracion_marbete',
            'lote_produccion_marbete',
            'url',
            # Datos del producto en el marbete
            'nombre_marca',
            'tipo_producto',
            'graduacion_alcoholica',
            'capacidad',
            'origen_del_producto',
            'fecha_importacion',
            'nombre_fabricante',
            'rfc_fabricante',
            'fecha_registro',
            # Datos obligatorios ingresados por el usuario
            'peso_cristal',
            'precio_unitario',
            'ingrediente'

        )


    def validate_peso_cristal(self, value):
        """ Validamos que el campo de 'peso_cristal' no esté vacío """

        if value is None:
            raise serializers.ValidationError("Es necesario ingresar el peso del cristal.")
        
        return value


    def validate_precio_unitario(self, value):
        """ Validamos que el campo 'precio_unitario' no esté vacío """ 
        if not value:
        #if value is None:
            raise serializers.ValidationError("Es necesario ingresar el precio unitario.")
        
        return value


#------------------------------------------------------------------
"""
-------------------------------------------------------------------
Serializador para crear un Producto importado
- El peso del cristal es proporcionado por el usuario
- El peso de la botella nueva se calcula a partor del peso del cristal
-------------------------------------------------------------------
"""
class ProductoImportadoWriteSerializer(serializers.ModelSerializer):

    ingrediente = serializers.PrimaryKeyRelatedField(read_only=False, queryset=models.Ingrediente.objects.all())

    class Meta:
        model = models.Producto
        fields = (
            'id',
            # Datos del marbete
            'folio',
            'tipo_marbete',
            'fecha_elaboracion_marbete',
            'lote_produccion_marbete',
            'url',
            # Datos del producto en el marbete
            'nombre_marca',
            'tipo_producto',
            'graduacion_alcoholica',
            'capacidad',
            'origen_del_producto',
            'fecha_importacion',
            'numero_pedimento',
            'nombre_fabricante',
            'rfc_fabricante',
            'fecha_registro',
            # Datos obligatorios ingresados por el usuario
            'peso_cristal',
            'precio_unitario',
            'ingrediente'

        )


    def validate_peso_cristal(self, value):
        """ Validamos que el campo de 'peso_cristal' no esté vacío """

        if value is None:
            raise serializers.ValidationError("Es necesario ingresar el peso del cristal.")
        
        return value
       


    def validate_precio_unitario(self, value):
        """ Validamos que el campo 'precio_unitario' no esté vacío """ 
        if not value:
        #if value is None:
            raise serializers.ValidationError("Es necesario ingresar el precio unitario.")
        
        return value

    def create(self, validated_data):

        # Calculamos 'peso_nueva' a partir del peso del cristal, su capacidad y la densidad del ingrediente
        peso_cristal = validated_data.get('peso_cristal')
        capacidad = validated_data.get('capacidad')
        ingrediente = validated_data.get('ingrediente')
        factor_peso = ingrediente.factor_peso
        peso_nueva = peso_cristal + (capacidad * factor_peso)

        # Creamos el Producto
        producto = models.Producto.objects.create(
            folio=validated_data.get('folio'),
            tipo_marbete=validated_data.get('tipo_marbete'),
            fecha_elaboracion_marbete=validated_data.get('fecha_elaboracion_marbete'),
            lote_produccion_marbete=validated_data.get('lote_produccion_marbete'),
            url=validated_data.get('url'),
            
            # Datos del producto en marbete
            nombre_marca=validated_data.get('nombre_marca'),
            tipo_producto=validated_data.get('tipo_producto'),
            graduacion_alcoholica=validated_data.get('graduacion_alcoholica'),
            capacidad=validated_data.get('capacidad'),
            origen_del_producto=validated_data.get('origen_del_producto'),
            fecha_importacion=validated_data.get('fecha_importacion'),
            numero_pedimento=validated_data.get('numero_pedimento'),
            nombre_fabricante=validated_data.get('nombre_fabricante'),
            rfc_fabricante=validated_data.get('rfc_fabricante'),

            # Datos registrados con app movil
            peso_nueva=peso_nueva,
            peso_cristal=validated_data.get('peso_cristal'),
            precio_unitario=validated_data.get('precio_unitario'),
            ingrediente=validated_data.get('ingrediente'),
        )

        return producto


#------------------------------------------------------------------
"""
-------------------------------------------------------------------
Serializador para crear un Producto nacional
-------------------------------------------------------------------
"""
class ProductoNacionalWriteSerializer(serializers.ModelSerializer):

    ingrediente = serializers.PrimaryKeyRelatedField(read_only=False, queryset=models.Ingrediente.objects.all())

    class Meta:
        model = models.Producto
        fields = (
            'id',
            # Datos del marbete
            'folio',
            'tipo_marbete',
            'fecha_elaboracion_marbete',
            'lote_produccion_marbete',
            'url',
            # Datos del producto en el marbete
            'nombre_marca',
            'tipo_producto',
            'graduacion_alcoholica',
            'capacidad',
            'origen_del_producto',
            'fecha_envasado',
            'lote_produccion',
            'nombre_fabricante',
            'rfc_fabricante',
            'fecha_registro',
            # Datos obligatorios ingresados por el usuario
            'peso_cristal',
            'precio_unitario',
            'ingrediente'

        )


    def validate_peso_cristal(self, value):
        """ Validamos que el campo de 'peso_cristal' no esté vacío """

        if value is None:
            raise serializers.ValidationError("Es necesario ingresar el peso del cristal.")
        
        return value


    def validate_precio_unitario(self, value):
        """ Validamos que el campo 'precio_unitario' no esté vacío """ 
        if not value:
        #if value is None:
            raise serializers.ValidationError("Es necesario ingresar el precio unitario.")
        
        return value

    def create(self, validated_data):

        # Calculamos 'peso_nueva' a partir del peso del cristal, su capacidad y la densidad del ingrediente
        peso_cristal = validated_data.get('peso_cristal')
        capacidad = validated_data.get('capacidad')
        ingrediente = validated_data.get('ingrediente')
        factor_peso = ingrediente.factor_peso
        peso_nueva = peso_cristal + (capacidad * factor_peso)

        # Creamos el Producto
        producto = models.Producto.objects.create(
            folio=validated_data.get('folio'),
            tipo_marbete=validated_data.get('tipo_marbete'),
            fecha_elaboracion_marbete=validated_data.get('fecha_elaboracion_marbete'),
            lote_produccion_marbete=validated_data.get('lote_produccion_marbete'),
            url=validated_data.get('url'),
            
            # Datos del producto en marbete
            nombre_marca=validated_data.get('nombre_marca'),
            tipo_producto=validated_data.get('tipo_producto'),
            graduacion_alcoholica=validated_data.get('graduacion_alcoholica'),
            capacidad=validated_data.get('capacidad'),
            origen_del_producto=validated_data.get('origen_del_producto'),
            fecha_envasado=validated_data.get('fecha_envasado'),
            lote_produccion=validated_data.get('lote_produccion'),
            nombre_fabricante=validated_data.get('nombre_fabricante'),
            rfc_fabricante=validated_data.get('rfc_fabricante'),

            # Datos registrados con app movil
            peso_nueva=peso_nueva,
            peso_cristal=validated_data.get('peso_cristal'),
            precio_unitario=validated_data.get('precio_unitario'),
            ingrediente=validated_data.get('ingrediente'),
        )

        return producto


#------------------------------------------------------------------
"""
-------------------------------------------------------------------
Serializador para crear un Producto importado, registrando el peso
de la botella nueva (sin tapa)
-------------------------------------------------------------------
"""
class ProductoImportadoFullWriteSerializer(serializers.ModelSerializer):

    ingrediente = serializers.PrimaryKeyRelatedField(read_only=False, queryset=models.Ingrediente.objects.all())

    class Meta:
        model = models.Producto
        fields = (
            'id',
            # Datos del marbete
            'folio',
            'tipo_marbete',
            'fecha_elaboracion_marbete',
            'lote_produccion_marbete',
            'url',
            # Datos del producto en el marbete
            'nombre_marca',
            'tipo_producto',
            'graduacion_alcoholica',
            'capacidad',
            'origen_del_producto',
            'fecha_importacion',
            'numero_pedimento',
            'nombre_fabricante',
            'rfc_fabricante',
            'fecha_registro',
            # Datos obligatorios ingresados por el usuario
            #'peso_cristal',
            'peso_nueva',
            'precio_unitario',
            'ingrediente'

        )


    def validate_peso_nueva(self, value):
        """ Validamos que el campo de 'peso_nueva' no esté vacío """

        if value is None:
            raise serializers.ValidationError("Es necesario ingresar el peso de la botella nueva sin tapa.")
        
        return value


    def validate_precio_unitario(self, value):
        """ Validamos que el campo 'precio_unitario' no esté vacío """ 
        if not value:
        #if value is None:
            raise serializers.ValidationError("Es necesario ingresar el precio unitario.")
        
        return value

    def create(self, validated_data):

        # Calculamos el peso del cristal a partir del peso de la botella nueva sin tapa
        peso_nueva = validated_data.get('peso_nueva')
        capacidad = validated_data.get('capacidad')
        ingrediente = validated_data.get('ingrediente')
        factor_peso = ingrediente.factor_peso
        peso_cristal = peso_nueva - (capacidad * factor_peso)

        # Creamos el Producto
        producto = models.Producto.objects.create(
            folio=validated_data.get('folio'),
            tipo_marbete=validated_data.get('tipo_marbete'),
            fecha_elaboracion_marbete=validated_data.get('fecha_elaboracion_marbete'),
            lote_produccion_marbete=validated_data.get('lote_produccion_marbete'),
            url=validated_data.get('url'),
            
            # Datos del producto en marbete
            nombre_marca=validated_data.get('nombre_marca'),
            tipo_producto=validated_data.get('tipo_producto'),
            graduacion_alcoholica=validated_data.get('graduacion_alcoholica'),
            capacidad=validated_data.get('capacidad'),
            origen_del_producto=validated_data.get('origen_del_producto'),
            fecha_importacion=validated_data.get('fecha_importacion'),
            numero_pedimento=validated_data.get('numero_pedimento'),
            nombre_fabricante=validated_data.get('nombre_fabricante'),
            rfc_fabricante=validated_data.get('rfc_fabricante'),

            # Datos registrados con app movil
            peso_nueva=validated_data.get('peso_nueva'),
            peso_cristal=peso_cristal,
            precio_unitario=validated_data.get('precio_unitario'),
            ingrediente=validated_data.get('ingrediente'),
        )

        return producto

#------------------------------------------------------------------
"""
-------------------------------------------------------------------
Serializador para crear un Producto nacional, registrando el peso
de la botella nueva (sin tapa)
-------------------------------------------------------------------
"""
class ProductoNacionalFullWriteSerializer(serializers.ModelSerializer):

    ingrediente = serializers.PrimaryKeyRelatedField(read_only=False, queryset=models.Ingrediente.objects.all())

    class Meta:
        model = models.Producto
        fields = (
            'id',
            # Datos del marbete
            'folio',
            'tipo_marbete',
            'fecha_elaboracion_marbete',
            'lote_produccion_marbete',
            'url',
            # Datos del producto en el marbete
            'nombre_marca',
            'tipo_producto',
            'graduacion_alcoholica',
            'capacidad',
            'origen_del_producto',
            'fecha_importacion',
            'numero_pedimento',
            'nombre_fabricante',
            'rfc_fabricante',
            'fecha_registro',
            # Datos obligatorios ingresados por el usuario
            #'peso_cristal',
            'peso_nueva',
            'precio_unitario',
            'ingrediente'

        )


    def validate_peso_nueva(self, value):
        """ Validamos que el campo de 'peso_nueva' no esté vacío """

        if value is None:
            raise serializers.ValidationError("Es necesario ingresar el peso de la botella nueva sin tapa.")
        
        return value


    def validate_precio_unitario(self, value):
        """ Validamos que el campo 'precio_unitario' no esté vacío """ 
        if not value:
        #if value is None:
            raise serializers.ValidationError("Es necesario ingresar el precio unitario.")
        
        return value

    def create(self, validated_data):

        # Calculamos el peso del cristal a partir del peso de la botella nueva sin tapa
        peso_nueva = validated_data.get('peso_nueva')
        capacidad = validated_data.get('capacidad')
        ingrediente = validated_data.get('ingrediente')
        factor_peso = ingrediente.factor_peso
        peso_cristal = peso_nueva - (capacidad * factor_peso)

        # Creamos el Producto
        producto = models.Producto.objects.create(
            folio=validated_data.get('folio'),
            tipo_marbete=validated_data.get('tipo_marbete'),
            fecha_elaboracion_marbete=validated_data.get('fecha_elaboracion_marbete'),
            lote_produccion_marbete=validated_data.get('lote_produccion_marbete'),
            url=validated_data.get('url'),
            
            # Datos del producto en marbete
            nombre_marca=validated_data.get('nombre_marca'),
            tipo_producto=validated_data.get('tipo_producto'),
            graduacion_alcoholica=validated_data.get('graduacion_alcoholica'),
            capacidad=validated_data.get('capacidad'),
            origen_del_producto=validated_data.get('origen_del_producto'),
            fecha_importacion=validated_data.get('fecha_importacion'),
            numero_pedimento=validated_data.get('numero_pedimento'),
            nombre_fabricante=validated_data.get('nombre_fabricante'),
            rfc_fabricante=validated_data.get('rfc_fabricante'),

            # Datos registrados con app movil
            peso_nueva=validated_data.get('peso_nueva'),
            peso_cristal=peso_cristal,
            precio_unitario=validated_data.get('precio_unitario'),
            ingrediente=validated_data.get('ingrediente'),
        )

        return producto


#------------------------------------------------------------------
"""
-------------------------------------------------------------------
Serializador para crear un Producto

- Funciona con productos nacionales o importados
- Si el cliente proporciona solo el peso del cristal, calcula el peso de la botella nueva
- Si el cliente proporciona solo el peso de la botella nueva, calcula el peso del cristal

-------------------------------------------------------------------
"""
class ProductoUniversalWriteSerializer(serializers.ModelSerializer):

    ingrediente = serializers.PrimaryKeyRelatedField(read_only=False, queryset=models.Ingrediente.objects.all())

    class Meta:
        model = models.Producto
        fields = (
            'id',
            # Datos del marbete
            'folio',
            'tipo_marbete',
            'fecha_elaboracion_marbete',
            'lote_produccion_marbete',
            'url',
            # Datos del producto en el marbete
            'nombre_marca',
            'tipo_producto',
            'graduacion_alcoholica',
            'capacidad',
            'origen_del_producto',
            'fecha_importacion',
            'fecha_envasado',
            'numero_pedimento',
            'lote_produccion',
            'nombre_fabricante',
            'rfc_fabricante',
            'fecha_registro',
            # Datos obligatorios ingresados por el usuario
            #'peso_cristal',
            'peso_nueva',
            'peso_cristal',
            'precio_unitario',
            'ingrediente'

        )
        
        extra_kwargs = {
            'fecha_importacion': {'required': False},
            'fecha_envasado': {'required': False},
            'numero_pedimento': {'required': False},
            'lote_produccion': {'required': False},
        }


    def validate_precio_unitario(self, value):
        """ Validamos que el campo 'precio_unitario' no esté vacío """ 
        if not value:
        #if value is None:
            raise serializers.ValidationError("Es necesario ingresar el precio unitario.")
        
        return value

    def create(self, validated_data):

        # Si el cliente proporciona el peso del cristal, calculamos el peso de la botella nueva
        peso_cristal = validated_data.get('peso_cristal')
        if peso_cristal is not None:

            capacidad = validated_data.get('capacidad')
            ingrediente = validated_data.get('ingrediente')
            factor_peso = ingrediente.factor_peso
            peso_nueva = round(peso_cristal + (capacidad * factor_peso))

        # Si el cliente proporciona el peso de la botella nueva sin tapa, calculamos el peso del cristal
        else:

            peso_nueva = validated_data.get('peso_nueva')
            capacidad = validated_data.get('capacidad')
            ingrediente = validated_data.get('ingrediente')
            factor_peso = ingrediente.factor_peso
            peso_cristal = round(peso_nueva - (capacidad * factor_peso))

        # Si el Producto es nacional, lo registramos con los atributos adhoc
        folio_sat = validated_data.get('folio')
        if folio_sat[0] == 'N':

            # Creamos el Producto nacional
            producto = models.Producto.objects.create(
                folio=validated_data.get('folio'),
                tipo_marbete=validated_data.get('tipo_marbete'),
                fecha_elaboracion_marbete=validated_data.get('fecha_elaboracion_marbete'),
                lote_produccion_marbete=validated_data.get('lote_produccion_marbete'),
                url=validated_data.get('url'),
                
                # Datos del producto en marbete
                nombre_marca=validated_data.get('nombre_marca'),
                tipo_producto=validated_data.get('tipo_producto'),
                graduacion_alcoholica=validated_data.get('graduacion_alcoholica'),
                capacidad=validated_data.get('capacidad'),
                origen_del_producto=validated_data.get('origen_del_producto'),
                #fecha_importacion=validated_data.get('fecha_importacion'),
                fecha_envasado=validated_data.get('fecha_envasado'),
                #numero_pedimento=validated_data.get('numero_pedimento'),
                lote_produccion=validated_data.get('lote_produccion'),
                nombre_fabricante=validated_data.get('nombre_fabricante'),
                rfc_fabricante=validated_data.get('rfc_fabricante'),

                # Datos registrados con app movil
                peso_nueva=peso_nueva,
                peso_cristal=peso_cristal,
                precio_unitario=validated_data.get('precio_unitario'),
                ingrediente=validated_data.get('ingrediente'),
            )

            return producto

        # Si el Producto es importado, lo registraos con los atributos adhoc
        else:

            # Creamos el Producto nacional
            producto = models.Producto.objects.create(
                folio=validated_data.get('folio'),
                tipo_marbete=validated_data.get('tipo_marbete'),
                fecha_elaboracion_marbete=validated_data.get('fecha_elaboracion_marbete'),
                lote_produccion_marbete=validated_data.get('lote_produccion_marbete'),
                url=validated_data.get('url'),
                
                # Datos del producto en marbete
                nombre_marca=validated_data.get('nombre_marca'),
                tipo_producto=validated_data.get('tipo_producto'),
                graduacion_alcoholica=validated_data.get('graduacion_alcoholica'),
                capacidad=validated_data.get('capacidad'),
                origen_del_producto=validated_data.get('origen_del_producto'),
                fecha_importacion=validated_data.get('fecha_importacion'),
                #fecha_envasado=validated_data.get('fecha_envasado'),
                numero_pedimento=validated_data.get('numero_pedimento'),
                #lote_produccion=validated_data.get('lote_produccion'),
                nombre_fabricante=validated_data.get('nombre_fabricante'),
                rfc_fabricante=validated_data.get('rfc_fabricante'),

                # Datos registrados con app movil
                peso_nueva=peso_nueva,
                peso_cristal=peso_cristal,
                precio_unitario=validated_data.get('precio_unitario'),
                ingrediente=validated_data.get('ingrediente'),
            )

            return producto


#------------------------------------------------------------------
class BotellaUpdateAlmacenSucursalSerializer(serializers.ModelSerializer):

    #sucursal = serializers.PrimaryKeyRelatedField(read_only=False, queryset=models.Sucursal.objects.all())
    #almacen = serializers.PrimaryKeyRelatedField(read_only=False, queryset=models.Almacen.objects.all())

    class Meta:
        model = models.Botella
        fields = (
            'folio',
            'ingrediente',
            'categoria',
            'peso_inicial',
            'precio_unitario',
            'proveedor',
            'fecha_registro',
            'estado',
            'almacen',
            'sucursal',
        )




class TraspasoWriteSerializer(serializers.ModelSerializer):

    botella = serializers.PrimaryKeyRelatedField(read_only=False, queryset=models.Botella.objects.all())
    #botella = BotellaUpdateAlmacenSucursalSerializer()
    sucursal = serializers.PrimaryKeyRelatedField(read_only=False, queryset=models.Sucursal.objects.all())
    almacen = serializers.PrimaryKeyRelatedField(read_only=False, queryset=models.Almacen.objects.all())

    class Meta:
        model = models.Traspaso
        fields = (
            'id',
            'botella',
            'sucursal',
            'almacen',
            #'usuario',
        )

    def create(self, validated_data):

        botella = validated_data.get('botella')
        sucursal = validated_data.get('sucursal')
        almacen = validated_data.get('almacen')

        #

        traspaso = models.Traspaso.objects.create(
            botella=botella,
            sucursal=sucursal,
            almacen=almacen,
        )

        botella.almacen = almacen
        botella.sucursal = sucursal
        botella.save()

        return traspaso


#------------------------------------------------------------------
class BotellaConsultaSerializer(serializers.ModelSerializer):

    class Meta: 
        model = models.Botella
        fields = '__all__'
        depth = 1


#------------------------------------------------------------------
class IngredienteWriteSerializer(serializers.ModelSerializer):

    categoria = serializers.PrimaryKeyRelatedField(read_only=False, queryset=models.Categoria.objects.all())

    class Meta:
        model = models.Ingrediente
        fields = '__all__'
        depth = 1


#------------------------------------------------------------------
class ProveedorSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Proveedor
        fields = '__all__'




"""
-------------------------------------------------------------------
Serializer que retorna los datos de un Producto
-------------------------------------------------------------------
"""
class ProductoSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Producto
        fields = '__all__'
        depth = 1


"""
-------------------------------------------------------------------
Serializer que construye una Botella nueva
-------------------------------------------------------------------
"""
class BotellaNuevaSerializer(serializers.ModelSerializer):

    almacen = serializers.PrimaryKeyRelatedField(read_only=False, queryset=models.Almacen.objects.all())
    sucursal = serializers.PrimaryKeyRelatedField(read_only=False, queryset=models.Sucursal.objects.all())
    usuario_alta = serializers.PrimaryKeyRelatedField(read_only=False, queryset=get_user_model().objects.all())
    producto = serializers.PrimaryKeyRelatedField(read_only=False, queryset=models.Producto.objects.all())
    proveedor = serializers.PrimaryKeyRelatedField(read_only=False, queryset=models.Proveedor.objects.all())

    class Meta:
        model = models.Botella
        fields = (
            'id',
            'almacen',
            'sucursal',
            'usuario_alta',
            'proveedor',
            'producto',
            'folio',
            'peso_nueva',
            'sat_hash'
        )

        extra_kwargs = {
            'peso_nueva': {'required': False},
            'folio': {'required': False}
        }

    def create(self, validated_data):

        peso_nueva = validated_data.get('peso_nueva')
        producto = validated_data.get('producto')
        ingrediente = producto.ingrediente
        precio_unitario = producto.precio_unitario
        capacidad = producto.capacidad
        factor_peso = ingrediente.factor_peso
        sat_hash = validated_data.get('sat_hash')

        # Si contamos con el peso de la botella medido con la bascula:
        if peso_nueva is not None:

            peso_inicial = peso_nueva
            peso_cristal = round(peso_nueva - (capacidad * factor_peso))

            # Si el blueprint no cuenta con 'peso_nueva', le asignamos uno de referencia temporal
            if producto.peso_nueva is None:
                
                producto.peso_nueva = peso_nueva
                producto.save()

        # Si no contamos con el peso medido con la bascula (pasa solo cuando registramos un vino de mesa):
        else:

            # Todos los blueprints de vinos de mesa deben por fuerza contar con 'peso_nueva'
            peso_nueva = producto.peso_nueva
            peso_inicial = producto.peso_nueva
            peso_cristal = round(peso_nueva - (capacidad * factor_peso))

        # Si el sat_hash es igual al folio del marbete, folio = sat_hash (botellas legacy)
        if ((sat_hash[0:2] == 'Nn') or (sat_hash[0:2] == 'Ii')) and (len(sat_hash) == 12):
            folio = sat_hash
        else:
            folio = ''

        botella = models.Botella.objects.create(

            # Datos tomados del blueprint y la bascula
            producto=producto,
            peso_nueva=peso_nueva,
            peso_inicial=peso_inicial,
            peso_cristal=peso_cristal,
            peso_actual=peso_inicial,
            precio_unitario=precio_unitario,

            # Datos del marbete:
            folio=folio,
            tipo_marbete='',
            fecha_elaboracion_marbete='',
            lote_produccion_marbete='',
            url='',
            sat_hash=sat_hash,

            # Datos del producto en marbete:
            nombre_marca='',
            tipo_producto='',
            graduacion_alcoholica='',
            capacidad=capacidad,
            origen_del_producto='',
            fecha_importacion='',
            fecha_envasado='',
            numero_pedimento='',
            lote_produccion='',
            nombre_fabricante='',
            rfc_fabricante='',

            # Datos adicionales:
            usuario_alta=validated_data.get('usuario_alta'),
            sucursal=validated_data.get('sucursal'),
            almacen=validated_data.get('almacen'),
            proveedor=validated_data.get('proveedor')

        )

        return botella


"""
-------------------------------------------------------------------
Serializer que construye una Producto nuevo sin necesidad de
tomar los datos obtenidos del SAT
-------------------------------------------------------------------
"""
class ProductoNuevoSerializer(serializers.ModelSerializer):

    ingrediente = serializers.PrimaryKeyRelatedField(read_only=False, queryset=models.Ingrediente.objects.all())

    class Meta:
        model = models.Producto
        fields = (
            'id',
            'ingrediente',
            'codigo_barras',
            'nombre_marca',
            'capacidad',
            'precio_unitario',
            'peso_nueva'
        )

    def create(self, validated_data):

        ingrediente = validated_data.get('ingrediente')
        factor_peso = ingrediente.factor_peso
        capacidad = validated_data.get('capacidad')
        peso_nueva = validated_data.get('peso_nueva')

        if peso_nueva is not None:
            peso_cristal = round(peso_nueva - (capacidad * factor_peso))

        else:
            peso_cristal =  None

        producto = models.Producto.objects.create(

            ingrediente=ingrediente,
            codigo_barras=validated_data.get('codigo_barras'),
            nombre_marca=validated_data.get('nombre_marca'),
            capacidad=capacidad,
            precio_unitario=validated_data.get('precio_unitario'),
            peso_nueva=peso_nueva,
            peso_cristal=peso_cristal,

            # Datos de la botella en el marbete
            tipo_producto='',
            graduacion_alcoholica='',
            origen_del_producto='',
            fecha_importacion='',
            fecha_envasado='',
            numero_pedimento='',
            lote_produccion='',
            nombre_fabricante='',
            rfc_fabricante='',

            # Datos del marbete:
            folio='',
            tipo_marbete='',
            fecha_elaboracion_marbete='',
            lote_produccion_marbete='',
            url='',
        )

        return producto


"""
-------------------------------------------------------------------
Serializer que retorna los datos de una Botella y su producto
asociado
-------------------------------------------------------------------
"""
class BotellaProductoSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Botella
        fields = (
            'id',
            'folio',
            'producto',
            'peso_nueva'
        )
        depth = 1


"""
-------------------------------------------------------------------
Serializer que construye una Botella usada
-------------------------------------------------------------------
"""
class BotellaUsadaSerializer(serializers.ModelSerializer):

    almacen = serializers.PrimaryKeyRelatedField(read_only=False, queryset=models.Almacen.objects.all())
    sucursal = serializers.PrimaryKeyRelatedField(read_only=False, queryset=models.Sucursal.objects.all())
    usuario_alta = serializers.PrimaryKeyRelatedField(read_only=False, queryset=get_user_model().objects.all())
    producto = serializers.PrimaryKeyRelatedField(read_only=False, queryset=models.Producto.objects.all())
    proveedor = serializers.PrimaryKeyRelatedField(read_only=False, queryset=models.Proveedor.objects.all())

    class Meta:
        model = models.Botella
        fields = (
            'id',
            'almacen',
            'sucursal',
            'usuario_alta',
            'proveedor',
            'producto',
            'folio',
            'peso_nueva',
            'peso_inicial',
            'sat_hash'
        )
        extra_kwargs = {'folio': {'required': False}}

    def create(self, validated_data):

        # Construimos los datos de peso de la botella
        peso_nueva = validated_data.get('peso_nueva')
        peso_inicial = validated_data.get('peso_inicial')
        producto = validated_data.get('producto')
        ingrediente = producto.ingrediente
        precio_unitario = producto.precio_unitario
        capacidad = producto.capacidad
        factor_peso = ingrediente.factor_peso
        peso_cristal = round(peso_nueva - (capacidad * factor_peso))
        estado_botella = '1'
        sat_hash = validated_data.get('sat_hash')

        # Creamos y guardamos la botella en la base de datos
        botella = models.Botella.objects.create(

            # Datos tomados del blueprint y la bascula
            producto=producto,
            peso_nueva=peso_nueva,
            peso_inicial=peso_inicial,
            peso_cristal=peso_cristal,
            peso_actual=peso_inicial,
            precio_unitario=precio_unitario,

            # Datos del marbete:
            folio='',
            tipo_marbete='',
            fecha_elaboracion_marbete='',
            lote_produccion_marbete='',
            url='',
            sat_hash=sat_hash,

            # Datos del producto en marbete:
            nombre_marca='',
            tipo_producto='',
            graduacion_alcoholica='',
            capacidad=capacidad,
            origen_del_producto='',
            fecha_importacion='',
            fecha_envasado='',
            numero_pedimento='',
            lote_produccion='',
            nombre_fabricante='',
            rfc_fabricante='',

            # Datos adicionales:
            usuario_alta=validated_data.get('usuario_alta'),
            sucursal=validated_data.get('sucursal'),
            almacen=validated_data.get('almacen'),
            proveedor=validated_data.get('proveedor'),
            estado=estado_botella,

        )

        return botella


"""
-------------------------------------------------------------------
Serializer que construye una Botella nueva cuando el usuario captura
manualmente el folio
-------------------------------------------------------------------
"""
class BotellaNuevaSerializerFolioManual(serializers.ModelSerializer):

    almacen = serializers.PrimaryKeyRelatedField(read_only=False, queryset=models.Almacen.objects.all())
    sucursal = serializers.PrimaryKeyRelatedField(read_only=False, queryset=models.Sucursal.objects.all())
    usuario_alta = serializers.PrimaryKeyRelatedField(read_only=False, queryset=get_user_model().objects.all())
    producto = serializers.PrimaryKeyRelatedField(read_only=False, queryset=models.Producto.objects.all())
    proveedor = serializers.PrimaryKeyRelatedField(read_only=False, queryset=models.Proveedor.objects.all())

    class Meta:
        model = models.Botella
        fields = (
            'id',
            'almacen',
            'sucursal',
            'usuario_alta',
            'proveedor',
            'producto',
            'folio',
            'peso_nueva',
            'sat_hash'
        )

        extra_kwargs = {
            'peso_nueva': {'required': False},
            'sat_hash': {'required': False},
            'folio': {'required': False}
        }

    """
    ---------------------------------------------------------------------------
    Validamos el folio capturado manualmente por el usuario
    ---------------------------------------------------------------------------
    """
    def validate_folio(self, value):

        # Si folio es un empty string, retornamos un error
        if value == '':
            raise serializers.ValidationError("El número de folio está vacío.")

        # Checamos la longitud del folio
        length_folio = len(value)

        """
        -----------------------------------------------------------------------------------
        Si el folio tiene entre 1 y 4 caracteres, asumimos que se trata de un folio custom:
        -----------------------------------------------------------------------------------
        """
        if length_folio >= 1 and length_folio <= 4:

            # Checamos que solo contenga digitos
            if re.match('^[0-9]*$', value):
                # Si solo contiene digitos, construimos el folio custom concatenando la sucursal y el folio capturado por el usuario
                #sucursal_id = validated_data.get('sucursal').id
                #sucursal_id = str(sucursal_id)
                #value = sucursal_id + value
                return value

            # Si no contiene solo digitos, retornamos un error
            raise serializers.ValidationError("El folio solo puede contener hasta 4 digitos del 0 al 9.")

        
        """
        ---------------------------------------------------------------------------
        Si el folio contiene 12 caracteres, asumimos que es un folio del SAT sin
        guion
        ---------------------------------------------------------------------------
        """
        # Checamos si el folio tiene 12 caracteres
        if length_folio == 12:
            # Tomamos los primeros dos caracteres del folio
            prefijo = value[:2]
            numero_folio = value[2:]

            # Checamos si los dos caracteres son de tipo folio nacional
            if re.match('(Nn|nN|nn|NN)', prefijo):
                prefijo = 'Nn'
                # Checamos si el numero del folio contiene solo digitos
                if re.match('^[0-9]*$', numero_folio):
                    # Construimos el folio normalizado
                    value = prefijo + numero_folio
                    return value
                # Si el numero de folio no contiene solo digitos, retornamos un error
                raise serializers.ValidationError("El folio del SAT debe tener solo 10 dígitos.")

            # Checamos si los dos caracteres son de tipo folio importado
            if re.match('(Ii|iI|ii|II)', prefijo):
                prefijo = 'Ii'
                # Checamos si el numero del folio contiene solo digitos
                if re.match('^[0-9]*$', numero_folio):
                    # Construimos el folio normalizado
                    value = prefijo + numero_folio
                    return value
                # Si el numero de folio no contiene solo digitos, retornamos un error
                raise serializers.ValidationError("El folio del SAT debe contener solo 10 dígitos.")
            
            # Si los dos caracteres no son de folio nacional o importado, retornamos error
            raise serializers.ValidationError("Los primeros dos caracteres del folio del SAT deben ser Nn o Ii.")

        """
        -----------------------------------------------------------------
        Si el folio es de 13 caracteres, asumimos que es un folio del SAT
        y que contiene al menos un guion
        -----------------------------------------------------------------
        """
        if length_folio == 13:
            # Eliminamos los guiones en el folio
            value = value.replace('-', '')

            # Si el folio resultante tiene menos de 12 caracteres, retornamos error
            if len(value) < 12:
                raise serializers.ValidationError('El folio del SAT solo debe contener un guion.')

            # Si el folio resultante sigue siendo de 13 caracteres, retornamos error
            if len(value) == 13:
                raise serializers.ValidationError('El folio del SAT no puede tener más de 12 caracteres')

            # Si el folio resultante es de 12 caracteres, continuamos

            # Tomamos los dos primeros caracteres del folio
            prefijo = value[:2]
            numero_folio = value[2:]

            # Checamos si los dos caracteres son de tipo folio nacional
            if re.match('(Nn|nN|nn|NN)', prefijo):
                prefijo = 'Nn'
                # Checamos si el numero de folio contiene solo digitos
                if re.match('^[0-9]*$', numero_folio):
                    # Construimos el folio normalizado
                    value = prefijo + numero_folio
                    return value

                # Si el numero de folio no contiene unicamente digitos, retornamos un error
                raise serializers.ValidationError('El folio del SAT debe contener solo 10 digitos.')

            # Checamos si los dos caracteres son de tipo folio importado
            if re.match('(Ii|iI|ii|II)', prefijo):
                prefijo = 'Ii'
                # Checamos si el numero de folio contiene solo digitos
                if re.match('^[0-9]*$', numero_folio):
                    # Construimos el folio normalizado
                    value = prefijo + numero_folio
                    return value

                # Si el numero de folio no contiene unicamente digitos, retornamos un error
                raise serializers.ValidationError('El folio del SAT debe contener solo 10 digitos.')

            # Si los dos caracteres no son de folio nacional o importado, retornamos un error
            raise serializers.ValidationError('Los primeros dos caracteres del folio del SAT deben ser Nn o Ii.')

        """
        --------------------------------------------------------------------------
        Si el folio tiene más de 4 caracteres, pero no tiene 12 ni 13 caracteres,
        retornamos un error
        --------------------------------------------------------------------------
        """
        raise serializers.ValidationError("El folio del SAT debe ser de 12 caracteres.")


    def create(self, validated_data):

        peso_nueva = validated_data.get('peso_nueva')
        producto = validated_data.get('producto')
        ingrediente = producto.ingrediente
        precio_unitario = producto.precio_unitario
        capacidad = producto.capacidad
        factor_peso = ingrediente.factor_peso
        sat_hash = validated_data.get('sat_hash')

        # Si contamos con el peso de la botella medido con la bascula:
        if peso_nueva is not None:

            peso_inicial = peso_nueva
            peso_cristal = round(peso_nueva - (capacidad * factor_peso))

            # Si el blueprint no cuenta con 'peso_nueva', le asignamos uno de referencia temporal
            if producto.peso_nueva is None:
                
                producto.peso_nueva = peso_nueva
                producto.save()

        # Si no contamos con el peso medido con la bascula (pasa solo cuando registramos un vino de mesa):
        else:

            # Todos los blueprints de vinos de mesa deben por fuerza contar con 'peso_nueva'
            peso_nueva = producto.peso_nueva
            peso_inicial = producto.peso_nueva
            peso_cristal = round(peso_nueva - (capacidad * factor_peso))

        if sat_hash is None:
            sat_hash = ''

        """
        -----------------------------------------------
        Procesamos los folios custom
        -----------------------------------------------
        """
        # Tomamos el folio del payload
        folio = validated_data.get('folio')

        # Tomamos el ID de la sucursal
        sucursal_id = str(validated_data.get('sucursal').id)

        # Si el folio es custom, le adjuntamos el ID de la sucursal
        if re.match('^[0-9]*$', folio):
            folio = sucursal_id + folio
        
        # Si el folio no es custom, lo dejamos como está
        else:
            folio = folio

        #-------------------------------------------------

        # Creamos la botella
        botella = models.Botella.objects.create(

            # Datos tomados del blueprint y la bascula
            producto=producto,
            peso_nueva=peso_nueva,
            peso_inicial=peso_inicial,
            peso_cristal=peso_cristal,
            peso_actual=peso_inicial,
            precio_unitario=precio_unitario,

            # Datos del marbete:
            folio=folio,
            tipo_marbete='',
            fecha_elaboracion_marbete='',
            lote_produccion_marbete='',
            url='',
            sat_hash=sat_hash,

            # Datos del producto en marbete:
            nombre_marca='',
            tipo_producto='',
            graduacion_alcoholica='',
            capacidad=capacidad,
            origen_del_producto='',
            fecha_importacion='',
            fecha_envasado='',
            numero_pedimento='',
            lote_produccion='',
            nombre_fabricante='',
            rfc_fabricante='',

            # Datos adicionales:
            usuario_alta=validated_data.get('usuario_alta'),
            sucursal=validated_data.get('sucursal'),
            almacen=validated_data.get('almacen'),
            proveedor=validated_data.get('proveedor')

        )

        return botella


"""
-------------------------------------------------------------------
Serializer que construye una Botella usada cuando el folio se
captura manualmente
-------------------------------------------------------------------
"""
class BotellaUsadaSerializerFolioManual(serializers.ModelSerializer):

    almacen = serializers.PrimaryKeyRelatedField(read_only=False, queryset=models.Almacen.objects.all())
    sucursal = serializers.PrimaryKeyRelatedField(read_only=False, queryset=models.Sucursal.objects.all())
    usuario_alta = serializers.PrimaryKeyRelatedField(read_only=False, queryset=get_user_model().objects.all())
    producto = serializers.PrimaryKeyRelatedField(read_only=False, queryset=models.Producto.objects.all())
    proveedor = serializers.PrimaryKeyRelatedField(read_only=False, queryset=models.Proveedor.objects.all())

    class Meta:
        model = models.Botella
        fields = (
            'id',
            'almacen',
            'sucursal',
            'usuario_alta',
            'proveedor',
            'producto',
            'folio',
            'peso_nueva',
            'peso_inicial',
            'sat_hash'
        )
        extra_kwargs = {'sat_hash': {'required': False}}

    """
    ---------------------------------------------------------------------------
    Validamos el folio capturado manualmente por el usuario
    ---------------------------------------------------------------------------
    """
    def validate_folio(self, value):

        # Si folio es un empty string, retornamos un error
        if value == '':
            raise serializers.ValidationError("El número de folio está vacío.")

        # Checamos la longitud del folio
        length_folio = len(value)

        """
        -----------------------------------------------------------------------------------
        Si el folio tiene entre 1 y 4 caracteres, asumimos que se trata de un folio custom:
        -----------------------------------------------------------------------------------
        """
        if length_folio <= 4:

            # Checamos que solo contenga digitos
            if re.match('^[0-9]*$', value):
                # Si solo contiene digitos, construimos el folio custom concatenando la sucursal y el folio capturado por el usuario
                #sucursal_id = validated_data.get('sucursal').id
                #sucursal_id = str(sucursal_id)
                #value = sucursal_id + value
                return value

            # Si no contiene solo digitos, retornamos un error
            raise serializers.ValidationError("El folio solo puede contener hasta 4 digitos del 0 al 9.")

        
        """
        ---------------------------------------------------------------------------
        Si el folio contiene 12 caracteres, asumimos que es un folio del SAT sin
        guion
        ---------------------------------------------------------------------------
        """
        # Checamos si el folio tiene 12 caracteres
        if length_folio == 12:
            # Tomamos los primeros dos caracteres del folio
            prefijo = value[:2]
            numero_folio = value[2:]

            # Checamos si los dos caracteres son de tipo folio nacional
            if re.match('(Nn|nN|nn|NN)', prefijo):
                prefijo = 'Nn'
                # Checamos si el numero del folio contiene solo digitos
                if re.match('^[0-9]*$', numero_folio):
                    # Construimos el folio normalizado
                    value = prefijo + numero_folio
                    return value
                # Si el numero de folio no contiene solo digitos, retornamos un error
                raise serializers.ValidationError("El folio del SAT debe tener solo 10 dígitos.")

            # Checamos si los dos caracteres son de tipo folio importado
            if re.match('(Ii|iI|ii|II)', prefijo):
                prefijo = 'Ii'
                # Checamos si el numero del folio contiene solo digitos
                if re.match('^[0-9]*$', numero_folio):
                    # Construimos el folio normalizado
                    value = prefijo + numero_folio
                    return value
                # Si el numero de folio no contiene solo digitos, retornamos un error
                raise serializers.ValidationError("El folio del SAT debe contener solo 10 dígitos.")
            
            # Si los dos caracteres no son de folio nacional o importado, retornamos error
            raise serializers.ValidationError("Los primeros dos caracteres del folio del SAT deben ser Nn o Ii.")

        """
        -----------------------------------------------------------------
        Si el folio es de 13 caracteres, asumimos que es un folio del SAT
        y que contiene al menos un guion
        -----------------------------------------------------------------
        """
        if length_folio == 13:
            # Eliminamos los guiones en el folio
            value = value.replace('-', '')

            # Si el folio resultante tiene menos de 12 caracteres, retornamos error
            if len(value) < 12:
                raise serializers.ValidationError('El folio del SAT solo debe contener un guion.')

            # Si el folio resultante sigue siendo de 13 caracteres, retornamos error
            if len(value) == 13:
                raise serializers.ValidationError('El folio del SAT no puede tener más de 12 caracteres')

            # Si el folio resultante es de 12 caracteres, continuamos

            # Tomamos los dos primeros caracteres del folio
            prefijo = value[:2]
            numero_folio = value[2:]

            # Checamos si los dos caracteres son de tipo folio nacional
            if re.match('(Nn|nN|nn|NN)', prefijo):
                prefijo = 'Nn'
                # Checamos si el numero de folio contiene solo digitos
                if re.match('^[0-9]*$', numero_folio):
                    # Construimos el folio normalizado
                    value = prefijo + numero_folio
                    return value

                # Si el numero de folio no contiene unicamente digitos, retornamos un error
                raise serializers.ValidationError('El folio del SAT debe contener solo 10 digitos.')

            # Checamos si los dos caracteres son de tipo folio importado
            if re.match('(Ii|iI|ii|II)', prefijo):
                prefijo = 'Ii'
                # Checamos si el numero de folio contiene solo digitos
                if re.match('^[0-9]*$', numero_folio):
                    # Construimos el folio normalizado
                    value = prefijo + numero_folio
                    return value

                # Si el numero de folio no contiene unicamente digitos, retornamos un error
                raise serializers.ValidationError('El folio del SAT debe contener solo 10 digitos.')

            # Si los dos caracteres no son de folio nacional o importado, retornamos un error
            raise serializers.ValidationError('Los primeros dos caracteres del folio del SAT deben ser Nn o Ii.')

        """
        --------------------------------------------------------------------------
        Si el folio tiene más de 4 caracteres, pero no tiene 12 ni 13 caracteres,
        retornamos un error
        --------------------------------------------------------------------------
        """
        raise serializers.ValidationError("El folio del SAT debe ser de 12 caracteres.")


    def create(self, validated_data):

        # Construimos los datos de peso de la botella
        peso_nueva = validated_data.get('peso_nueva')
        peso_inicial = validated_data.get('peso_inicial')
        producto = validated_data.get('producto')
        ingrediente = producto.ingrediente
        precio_unitario = producto.precio_unitario
        capacidad = producto.capacidad
        factor_peso = ingrediente.factor_peso
        peso_cristal = round(peso_nueva - (capacidad * factor_peso))
        estado_botella = '1'
        sat_hash = validated_data.get('sat_hash')

        """
        -----------------------------------------------
        Procesamos los folios custom
        -----------------------------------------------
        """
        # Tomamos el folio del payload
        folio = validated_data.get('folio')

        # Tomamos el ID de la sucursal
        sucursal_id = str(validated_data.get('sucursal').id)

        # Si el folio es custom, le adjuntamos el ID de la sucursal
        if re.match('^[0-9]*$', folio):
            folio = sucursal_id + folio
        
        # Si el folio no es custom, lo dejamos como está
        else:
            folio = folio

        # Creamos y guardamos la botella en la base de datos
        botella = models.Botella.objects.create(

            # Datos tomados del blueprint y la bascula
            producto=producto,
            peso_nueva=peso_nueva,
            peso_inicial=peso_inicial,
            peso_cristal=peso_cristal,
            peso_actual=peso_inicial,
            precio_unitario=precio_unitario,

            # Datos del marbete:
            folio=folio,
            tipo_marbete='',
            fecha_elaboracion_marbete='',
            lote_produccion_marbete='',
            url='',
            sat_hash=sat_hash,

            # Datos del producto en marbete:
            nombre_marca='',
            tipo_producto='',
            graduacion_alcoholica='',
            capacidad=capacidad,
            origen_del_producto='',
            fecha_importacion='',
            fecha_envasado='',
            numero_pedimento='',
            lote_produccion='',
            nombre_fabricante='',
            rfc_fabricante='',

            # Datos adicionales:
            usuario_alta=validated_data.get('usuario_alta'),
            sucursal=validated_data.get('sucursal'),
            almacen=validated_data.get('almacen'),
            proveedor=validated_data.get('proveedor'),
            estado=estado_botella,

        )

        return botella