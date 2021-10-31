from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
import os
from core import models
import pandas as pd
import numpy as np
from decimal import Decimal


class Command(BaseCommand):
    help = "Alta de marcas de botellas en el mercado"

    def add_arguments(self, parser):
        parser.add_argument('file', type=str, help='El nombre del archivo con los datos de las marcas')

    def handle(self, *args, **kwargs):
        
        csv_file = kwargs['file']

        try: 
            # Creamos un path para el archivo CSV
            path_csv = os.path.join(os.path.dirname(os.path.realpath(__file__)), csv_file)

        except FileNotFoundError:
            return self.stdout.write(self.style.ERROR('No se encontro el archivo {} \n'.format(csv_file)))

        else:
            # Construimos un dataframe con los datos del CSV e importamos todo como string
            df_blueprints = pd.read_csv(path_csv, dtype=str)

            # Creamos una lista para guardar todos los errores que ocirran durante el proceso
            lista_ingredientes_error = []

            contador = 0

            # Iteramos por las filas del dataframe
            for (codigo_barras, nombre_marca, codigo_ingrediente, capacidad, precio_unitario, peso_cristal, peso_nueva) in df_blueprints.itertuples(index=False, name=None):

                # Checamos que el Ingrediente exista
                try:
                    ingrediente = models.Ingrediente.objects.get(codigo=codigo_ingrediente)

                except ObjectDoesNotExist:
                    lista_ingredientes_error.append((codigo_barras, nombre_marca, codigo_ingrediente))
                    self.stdout.write(self.style.WARNING('El ingrediente {} no existe en la base de datos!\n'.format(codigo_ingrediente)))

                # Si el ingrediente existe creamos el blueprint
                else:
                    # Convertimos 'precio_unitario' a Decimal
                    precio_unitario = Decimal(float(precio_unitario))
                    # Convertimos 'capacidad' a int
                    capacidad = int(capacidad)

                    if  (pd.isna(peso_nueva) or (int(peso_nueva) == 0)) or (pd.isna(peso_cristal) or (int(peso_cristal) == 0))  :
                        peso_nueva = None
                        peso_cristal = None

                    else:
                        peso_cristal = int(peso_cristal)
                        peso_nueva = int(peso_nueva)

                    # Creamos el blueprint
                    models.Producto.objects.create(
                        folio='',
                        ingrediente=ingrediente,
                        codigo_barras=codigo_barras,

                        tipo_marbete='',
                        fecha_elaboracion_marbete='',
                        lote_produccion_marbete='',
                        url='',

                        nombre_marca=nombre_marca,
                        tipo_producto='',
                        graduacion_alcoholica='',
                        capacidad=capacidad,
                        origen_del_producto='',
                        fecha_envasado='',
                        fecha_importacion='',
                        lote_produccion='',
                        numero_pedimento='',
                        nombre_fabricante='',
                        rfc_fabricante='',

                        peso_nueva=peso_nueva,
                        peso_cristal=peso_cristal,
                        precio_unitario=precio_unitario,
                    )

                    contador = contador + 1

            self.stdout.write(self.style.SUCCESS('---------------------------------------------------\n'))
            self.stdout.write(self.style.SUCCESS('ALTA DE BLUEPRINTS TERMINADA\n'))
            self.stdout.write(self.style.SUCCESS('---------------------------------------------------\n'))
            self.stdout.write(self.style.SUCCESS('Se registraron un total de {} blueprints con exito\n'.format(contador)))
            self.stdout.write(self.style.WARNING('Se generaron {} errores causados por ingredientes no registrados\n'.format(len(lista_ingredientes_error))))

            # Si hay errores por ingredientes no registrados, lisar los blueprints afectados
            if len(lista_ingredientes_error) > 0:
                self.stdout.write(self.style.ERROR('---------------------------------------------------\n'))
                self.stdout.write(self.style.ERROR('---------------------------------------------------\n'))
                self.stdout.write(self.style.ERROR('BLUEPRINTS CON ERRORES\n'))
                self.stdout.write(self.style.ERROR('---------------------------------------------------\n'))
                self.stdout.write(self.style.ERROR('---------------------------------------------------\n'))

                for item in lista_ingredientes_error:
                    self.stdout.write(self.style.ERROR('---- > {}\n'.format(item)))

