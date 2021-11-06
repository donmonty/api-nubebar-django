from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from django.db import DatabaseError, transaction
from django.contrib.auth import get_user_model
from django.utils.timezone import make_aware
from core import models
from decimal import Decimal

import os
import pandas as pd
import datetime
import json
from freezegun import freeze_time


class Command(BaseCommand):
  help = 'Setup para demo de Inspeccion'

  def handle(self, *args, **kwargs):

    try:
      ## ===========================================
      ## SETUP
      ## ===========================================

      with transaction.atomic():
        # Fechas
        hoy = datetime.date.today()
        ayer = hoy - datetime.timedelta(days=1)

        # Proveedor
        vinos_america = models.Proveedor.objects.create(nombre='Vinos America')

        # Cliente
        operadora_pecos = models.Cliente.objects.create(nombre='Operadora Gama')
        # Sucursal
        pecos = models.Sucursal.objects.create(nombre='LA CABANA DE PECOS', cliente=operadora_pecos)
        # Almacen
        barra_1 = models.Almacen.objects.create(nombre='BARRA 1', numero=1, sucursal=pecos)
        # Caja
        caja_1 = models.Caja.objects.create(numero=1, nombre='CAJA 1', almacen=barra_1)
        # Usuario
        usuario = get_user_model().objects.create(email='test@nubebar.com', password='zelda')
        usuario.sucursales.add(pecos)

        # Categorias
        categoria_whisky = models.Categoria.objects.create(nombre='WHISKY')
        categoria_tequila = models.Categoria.objects.create(nombre='TEQUILA')

        # Ingredientes
        herradura_blanco = models.Ingrediente.objects.create(
          codigo='TEQU001',
          nombre='HERRADURA BLANCO',
          categoria=categoria_tequila,
          factor_peso=0.95
        )
        jw_black = models.Ingrediente.objects.create(
          codigo='WHIS001',
          nombre='JOHNNIE WALKER BLACK',
          categoria=categoria_whisky,
          factor_peso=0.95
        )

        # Recetas
        trago_herradura_blanco = models.Receta.objects.create(
          codigo_pos='19017',
          nombre='Copa Herradura Blanco',
          sucursal=pecos
        )
        trago_jw_black = models.Receta.objects.create(
          codigo_pos= '21006',
          nombre='Copa JW Black',
          sucursal=pecos
        )

        # Ingredientes-Recetas
        ir_herradura_blanco = models.IngredienteReceta.objects.create(
          receta=trago_herradura_blanco,
          ingrediente=herradura_blanco,
          volumen=60
        )
        ir_jw_black = models.IngredienteReceta.objects.create(
          receta=trago_jw_black,
          ingrediente=jw_black,
          volumen=60
        )



        # Ventas
        venta_herradura_blanco = models.Venta.objects.create(
          receta=trago_herradura_blanco,
          sucursal=pecos,
          fecha=ayer,
          unidades=1,
          importe=100,
          caja=caja_1
        )
        venta_jw_black = models.Venta.objects.create(
          receta=trago_jw_black,
          sucursal=pecos,
          fecha=ayer,
          unidades=1,
          importe=180,
          caja=caja_1
        )

        # Consumos Recetas Vendidas
        cr_herradura_blanco = models.ConsumoRecetaVendida.objects.create(
          ingrediente=herradura_blanco,
          receta=trago_herradura_blanco,
          venta=venta_herradura_blanco,
          fecha=ayer,
          volumen=60
        )
        cr_jw_black = models.ConsumoRecetaVendida.objects.create(
          ingrediente=jw_black,
          receta=trago_jw_black,
          venta=venta_jw_black,
          fecha=ayer,
          volumen=60
        )

        # Productos
        producto_herradura_blanco = models.Producto.objects.create(
          ingrediente=herradura_blanco,
          capacidad=700,
          peso_nueva=1115,
          peso_cristal=450,
          codigo_barras='0744607000109'
        )

        producto_jw_black = models.Producto.objects.create(
          ingrediente=jw_black,
          capacidad=750,
          peso_nueva=1113,
          peso_cristal=400,
          codigo_barras='5000267024004'
        )

        # Botellas
        botella_herradura_blanco = models.Botella.objects.create(
          folio='Nn1816767788',
          producto=producto_herradura_blanco,
          usuario_alta=usuario,
          sucursal=pecos,
          almacen=barra_1,
          proveedor=vinos_america,
          sat_hash='Nn1816767788',
          peso_cristal=450,
          peso_inicial=1115,
          peso_actual=1115
        )

        botella_jw_black = models.Botella.objects.create(
          folio='Ii0934665909',
          producto=producto_jw_black,
          usuario_alta=usuario,
          sucursal=pecos,
          almacen=barra_1,
          proveedor=vinos_america,
          sat_hash='Ii0934665909',
          peso_cristal=400,
          peso_inicial=1113,
          peso_actual=1113
        )

    except DatabaseError as error:
      raise CommandError('ERROR: {}'.format(error))

    self.stdout.write(self.style.SUCCESS('Inspection Demo ready!'))

    