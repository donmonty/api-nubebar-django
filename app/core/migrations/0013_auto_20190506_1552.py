# Generated by Django 2.1.8 on 2019-05-06 15:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_auto_20190426_1721'),
    ]

    operations = [
        migrations.AddField(
            model_name='botella',
            name='categoria',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='botella',
            name='ingrediente',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
