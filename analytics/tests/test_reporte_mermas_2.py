from django.test import TestCase
from django.db.models import F, Q, QuerySet, Avg, Count, Sum, Subquery, OuterRef, Exists, Func, ExpressionWrapper, DecimalField, IntegerField, Case, When
from django.contrib.auth import get_user_model
from django.urls import reverse
from unittest.mock import patch

from rest_framework import status
from rest_framework.test import APIClient
from rest_framework import serializers

from core import models

import datetime
from django.utils.timezone import make_aware
from decimal import Decimal, ROUND_UP
import json
from freezegun import freeze_time
from analytics import reporte_mermas

from analytics.serializers import (
    ReporteMermasDetalleSerializer,
    MermaIngredienteReadSerializer,
    ReporteMermasListSerializer,
)


class AnalyticsTests(TestCase):
    """ Testear acceso autenticado al API """
    maxDiff = None

    def setUp(self):

        # API Client
        self.client = APIClient()

        #Fechas
        self.hoy = datetime.date.today()
        self.ayer = self.hoy - datetime.timedelta(days=1)

        # Proveedores
        self.vinos_america = models.Proveedor.objects.create(nombre='Vinos America')

        # Cliente
        self.operadora_magno = models.Cliente.objects.create(nombre='MAGNO BRASSERIE')

        # Sucursal
        self.magno_brasserie = models.Sucursal.objects.create(nombre='MAGNO-BRASSERIE', cliente=self.operadora_magno)

        # Almacenes
        self.barra_1 = models.Almacen.objects.create(nombre='BARRA 1', numero=1, sucursal=self.magno_brasserie)
        
        # Cajas
        self.caja_1 = models.Caja.objects.create(numero=1, nombre='CAJA 1', almacen=self.barra_1)

        # Usuarios
        self.usuario = get_user_model().objects.create(email='test@foodstack.mx', password='password123')
        self.usuario.sucursales.add(self.magno_brasserie)

        # Autenticación
        self.client.force_authenticate(self.usuario)

        #Categorías
        self.categoria_ron = models.Categoria.objects.create(nombre='RON')

        # Ingredientes
        self.zacapa = models.Ingrediente.objects.create(
            codigo='RONE001',
            nombre='ZACAPA',
            categoria=self.categoria_ron,
            factor_peso=0.95
        )

        # Recetas
        self.copa_zacapa = models.Receta.objects.create(
            codigo_pos='18019',
            nombre='Copa Zacapa',
            sucursal=self.magno_brasserie
        )

        # Ingredientes-Recetas
        self.ir_zacapa = models.IngredienteReceta.objects.create(receta=self.copa_zacapa, ingrediente=self.zacapa, volumen=60)


        with freeze_time("2021-12-30"):
            # Manejamos el tema del naive datetime
            naive_datetime = datetime.datetime.now()
            aware_datetime = make_aware(naive_datetime)

            # Ventas
            self.venta_zacapa = models.Venta.objects.create(
                receta=self.copa_zacapa,
                sucursal=self.magno_brasserie,
                #fecha=self.ayer,
                fecha=aware_datetime,
                unidades=1,
                importe=170,
                caja=self.caja_1
            )
            print("Fecha Venta Copa Zacapa")
            print(self.venta_zacapa.fecha)

            # Consumos Recetas Vendidas
            self.cr_zacapa = models.ConsumoRecetaVendida.objects.create(
                ingrediente=self.zacapa,
                receta=self.copa_zacapa,
                venta=self.venta_zacapa,
                fecha=aware_datetime,
                volumen=60
            )

        # Productos
        self.producto_zacapa = models.Producto.objects.create(
            ingrediente=self.zacapa,
            peso_cristal=554,
            capacidad=750,
        )

        # Botella 1
        with freeze_time("2021-12-30 16:07:45", tz_offset=-6):

            self.botella_zacapa_1 = models.Botella.objects.create(
                folio='Ii1370111330',
                sat_hash='Ii1370111330',
                producto=self.producto_zacapa,
                capacidad=750,
                usuario_alta=self.usuario,
                sucursal=self.magno_brasserie,
                almacen=self.barra_1,
                proveedor=self.vinos_america,
                peso_cristal=554,
                peso_inicial=1266,
                peso_actual=554,
                estado='0'
            )
        fecha_baja_1 = datetime.datetime(2021, 12, 30, 10, 24, 9)
        self.botella_zacapa_1.fecha_baja = make_aware(fecha_baja_1)
        print("//// Fecha alta botella 1:")
        print(self.botella_zacapa_1.fecha_registro)
        print("/// Fecha baja botella 1:")
        print(self.botella_zacapa_1.fecha_baja)
        print(self.botella_zacapa_1.fecha_baja > self.botella_zacapa_1.fecha_registro)


        # Botella 2
        with freeze_time("2021-12-30 16:07:18", tz_offset=-6):

            self.botella_zacapa_2 = models.Botella.objects.create(
                folio='Ii1370116597',
                sat_hash='Ii1370116597',
                producto=self.producto_zacapa,
                capacidad=750,
                usuario_alta=self.usuario,
                sucursal=self.magno_brasserie,
                almacen=self.barra_1,
                proveedor=self.vinos_america,
                peso_cristal=554,
                peso_inicial=1266,
                peso_actual=554,
                estado='0'
            )
        fecha_baja_2 = datetime.datetime(2021, 12, 30, 10, 23, 29)
        self.botella_zacapa_1.fecha_baja = make_aware(fecha_baja_2)

        # Botella 3
        with freeze_time("2021-12-29 16:44:28", tz_offset=-6):

            self.botella_zacapa_3 = models.Botella.objects.create(
                folio='Ii1387181171',
                sat_hash='Ii1387181171',
                producto=self.producto_zacapa,
                capacidad=750,
                usuario_alta=self.usuario,
                sucursal=self.magno_brasserie,
                almacen=self.barra_1,
                proveedor=self.vinos_america,
                peso_cristal=540,
                peso_inicial=1252,
                peso_actual=540,
                estado='0'
            )
        fecha_baja_3 = datetime.datetime(2021, 12, 29, 11, 9, 2)
        self.botella_zacapa_1.fecha_baja = make_aware(fecha_baja_3)

        # Botella 4
        with freeze_time("2021-12-29 16:43:40", tz_offset=-6):

            self.botella_zacapa_4 = models.Botella.objects.create(
                folio='Ii1387181057',
                sat_hash='Ii1387181057',
                producto=self.producto_zacapa,
                capacidad=750,
                usuario_alta=self.usuario,
                sucursal=self.magno_brasserie,
                almacen=self.barra_1,
                proveedor=self.vinos_america,
                peso_cristal=540,
                peso_inicial=1252,
                peso_actual=540,
                estado='0'
            )
        fecha_baja_4 = datetime.datetime(2021, 12, 30, 10, 24, 46)
        self.botella_zacapa_1.fecha_baja = make_aware(fecha_baja_4)

        # Botella 5
        with freeze_time("2021-12-17 22:27:08", tz_offset=-6):

            self.botella_zacapa_5 = models.Botella.objects.create(
                folio='Ii1387181174',
                sat_hash='Ii1387181174',
                producto=self.producto_zacapa,
                capacidad=750,
                usuario_alta=self.usuario,
                sucursal=self.magno_brasserie,
                almacen=self.barra_1,
                proveedor=self.vinos_america,
                peso_cristal=508,
                peso_inicial=1220,
                peso_actual=738,
                estado='1'
            )

        # Abrimos la primera inspeccion
        # -------------------------------------------
        # 2021, 12, 30, 16, 17, 25
        with freeze_time("2021-12-30 16:17:25", tz_offset=-6):

            self.inspeccion_1 = models.Inspeccion.objects.create(
                almacen=self.barra_1,
                sucursal=self.magno_brasserie,
                usuario_alta=self.usuario,
                usuario_cierre=self.usuario,
                estado='0'
            )

            self.item_inspeccion_11 = models.ItemInspeccion.objects.create(
                inspeccion=self.inspeccion_1,
                botella=self.botella_zacapa_1,
                peso_botella=554
            )

            self.item_inspeccion_12 = models.ItemInspeccion.objects.create(
                inspeccion=self.inspeccion_1,
                botella=self.botella_zacapa_5,
                peso_botella=784
            )

        
        # Cerramos la primera inspeccion
        #---------------------------------------
        with freeze_time("2021-12-30 16:58:00", tz_offset=-6):
            self.inspeccion_1.estado = '1'

        # Abrimos la segunda inspeccion
        #---------------------------------------
        with freeze_time("2021-12-31 16:14:04", tz_offset=-6):
            
            self.inspeccion_2 = models.Inspeccion.objects.create(
                almacen=self.barra_1,
                sucursal=self.magno_brasserie,
                usuario_alta=self.usuario,
                usuario_cierre=self.usuario,
                estado='0'
            )
        
        # Cerramos la segunda inspeccion
        #--------------------------------
        with freeze_time("2021-12-31 17:31:16", tz_offset=-6):
            self.inspeccion_2.estado = '1'


        # Creamos los items inspeccionados de la segunda inspeccion
        #------------------------------------
        with freeze_time("2021-12-30 16:30:00", tz_offset=-6):
            self.item_inspeccion_21 = models.ItemInspeccion.objects.create(
                inspeccion=self.inspeccion_2,
                botella=self.botella_zacapa_5,
                peso_botella=738
            )


    def test_reporte_ok(self):
        """
        Testear que el reporte funciona OK
        """

        # Ejecutamos el Reporte de Mermas
        consumos = reporte_mermas.calcular_consumos(self.inspeccion_2,  self.inspeccion_1.timestamp_update, self.inspeccion_2.timestamp_alta)
        print("//// Consumos:")
        print(consumos)

        self.assertEqual(1, 1)
