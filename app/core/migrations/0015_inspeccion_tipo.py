# Generated by Django 2.1.8 on 2019-06-11 16:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_iteminspeccion_inspeccionado'),
    ]

    operations = [
        migrations.AddField(
            model_name='inspeccion',
            name='tipo',
            field=models.CharField(choices=[('0', 'DIARIA'), ('1', 'TOTAL')], default='0', max_length=1),
        ),
    ]
