# Generated by Django 3.2.13 on 2022-06-28 07:41

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('social', '0004_auto_20220603_1024'),
    ]

    operations = [
        migrations.AlterField(
            model_name='socialaccount',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='socialprovider',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
