# Generated by Django 3.2.13 on 2022-06-28 07:41

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('user', '0003_auto_20211215_1255'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailuser',
            name='first_name',
            field=models.CharField(blank=True, max_length=150, verbose_name='first name'),
        ),
        migrations.AlterField(
            model_name='emailuser',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
