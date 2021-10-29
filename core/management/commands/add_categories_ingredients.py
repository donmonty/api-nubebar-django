from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
import os
import sys
import errno
from core import models
import pandas as pd


class Seeder():

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def crear_categorias(self):

        nombres_categorias = [
            'BRANDY',
            'COGNAC',
            'GINEBRA',
            'LICOR',
            'MEZCAL',
            'RON',
            'SAKE',
            'TEQUILA',
            'VINO BLANCO',
            'VINO ESPUMOSO',
            'VINO TINTO',
            'VODKA',
            'WHISKY'
        ]

        contador = 0

        for nombre in nombres_categorias:

            # Checamos que no exista una Categoria con el mismo nombre antes de crearla
            try:
                categoria = models.Categoria.objects.get(nombre=nombre)
                sys.stdout.write('Ya existe una Categoria llamada {}\n'.format(nombre))
                sys.stdout.write('---------------------------------------------------------\n')

            # Si la Categoria no existe, la creamos
            except ObjectDoesNotExist:
                categoria = models.Categoria.objects.create(nombre=nombre)
                contador = contador + 1
                sys.stdout.write('Categoria {} creada con exito!\n'.format(nombre))

        sys.stdout.write('---------------------------------------------------------\n')
        sys.stdout.write('Se crearon {} categorias\n'.format(contador))


    def crear_ingredientes(self, csv_name):

        try:
            # Guardamos el CSV de los ingredientes en un dataframe
            path_csv = os.path.join(os.path.dirname(os.path.realpath(__file__)), csv_name)
            df_ingredientes = pd.read_csv(path_csv)

            # Creamos una variable para llevar la cuenta de los ingredientes creados
            contador = 0

            # Iteramos por el dataframe y convertimos cada fila en un ingrediente
            for (nombre, codigo, categoria, factor_peso) in df_ingredientes.itertuples(index=False, name=None):

                # Tomamos la Categoria que le asignaremos al Ingrediente
                categoria = models.Categoria.objects.get(nombre=categoria)
                # Creamos el Ingrediente
                ingrediente = models.Ingrediente.objects.create(
                    nombre=nombre,
                    codigo=codigo,
                    categoria=categoria,
                    factor_peso=factor_peso
                )
                contador = contador + 1
                #sys.stdout.write('{} creado con exito!'.format(ingrediente.nombre))

            sys.stdout.write('---------------------------------------------------------\n')
            sys.stdout.write('Operacion exitosa!\n')
            sys.stdout.write('Se crearon {} ingredientes'.format(contador))

            return {"status": "OK"}

        except FileNotFoundError as error:
            sys.stdout.write('ERROR: {}\n'.format(error.args[1]))
            sys.stdout.write('No se encontro el archivo de Ingredientes llamado {}!\n'.format(csv_name))


class Command(BaseCommand):

    help = "Alta inicial de Categorias e Ingredientes"

    def add_arguments(self, parser):
        parser.add_argument('file', type=str, help='El nombre del archivo CSV con los datos de Ingredientes')

    def handle(self, *args, **kwargs):

        csv_file = kwargs['file']

        seeder = Seeder()

        seeder.crear_categorias()
        self.stdout.write('---------------------------------------------------------\n')
        self.stdout.write('---------------------------------------------------------\n')
        self.stdout.write('---------------------------------------------------------\n')
        ingredientes_status = seeder.crear_ingredientes(csv_file)

        try:
            status = ingredientes_status['status']
            self.stdout.write(self.style.SUCCESS("Operacion exitosa!"))

        except:
            self.stdout.write(self.style.WARNING("Hubo un error!"))

