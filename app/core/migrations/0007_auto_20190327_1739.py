# Generated by Django 2.1.7 on 2019-03-27 17:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_producto'),
    ]

    operations = [
        migrations.CreateModel(
            name='Botella',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('folio', models.CharField(max_length=12, unique=True)),
                ('tipo_marbete', models.CharField(blank=True, max_length=255)),
                ('fecha_elaboracion_marbete', models.CharField(blank=True, max_length=255)),
                ('lote_produccion_marbete', models.CharField(blank=True, max_length=255)),
                ('url', models.URLField(blank=True, max_length=255)),
                ('nombre_marca', models.CharField(blank=True, max_length=255)),
                ('tipo_producto', models.CharField(blank=True, max_length=255)),
                ('graduacion_alcoholica', models.CharField(blank=True, max_length=255)),
                ('capacidad', models.IntegerField(blank=True, null=True)),
                ('origen_del_producto', models.CharField(blank=True, max_length=255)),
                ('fecha_importacion', models.CharField(blank=True, max_length=255)),
                ('nombre_fabricante', models.CharField(blank=True, max_length=255)),
                ('rfc_fabricante', models.CharField(blank=True, max_length=255)),
                ('estado', models.CharField(choices=[('2', 'NUEVA'), ('1', 'CON LIQUIDO'), ('0', 'VACIA')], default='2', max_length=1)),
                ('fecha_registro', models.DateTimeField(auto_now_add=True)),
                ('fecha_baja', models.DateTimeField(blank=True, default=None, null=True)),
                ('peso_cristal', models.IntegerField(blank=True, default=0, null=True)),
                ('peso_inicial', models.IntegerField(blank=True, default=0, null=True)),
                ('precio_unitario', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
                ('almacen', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='botellas_almacen', to='core.Almacen')),
                ('producto', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='botellas', to='core.Producto')),
            ],
        ),
        migrations.CreateModel(
            name='Proveedor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=255)),
                ('razon_social', models.CharField(blank=True, max_length=255)),
                ('rfc', models.CharField(blank=True, max_length=13)),
                ('direccion', models.TextField(blank=True, max_length=500)),
                ('ciudad', models.CharField(blank=True, max_length=255)),
            ],
        ),
        migrations.AddField(
            model_name='botella',
            name='proveedor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='botellas_proveedor', to='core.Proveedor'),
        ),
        migrations.AddField(
            model_name='botella',
            name='sucursal',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='botellas_sucursal', to='core.Sucursal'),
        ),
        migrations.AddField(
            model_name='botella',
            name='usuario_alta',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
    ]
