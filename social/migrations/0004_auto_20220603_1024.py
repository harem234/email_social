# Generated by Django 2.2.23 on 2022-06-03 05:54

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('social', '0003_auto_20211215_1255'),
    ]

    operations = [
        migrations.AlterField(
            model_name='socialaccount',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='socialprovider',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
