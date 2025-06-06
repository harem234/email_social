# Generated by Django 5.2.1 on 2025-05-23 21:10

import django.db.models.deletion
import social.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('social', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='socialaccount',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='socialaccount_user', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddConstraint(
            model_name='socialprovider',
            constraint=models.UniqueConstraint(fields=('social', 'client_id'), name='every client_id  per social is unique'),
        ),
        migrations.AddField(
            model_name='socialaccount',
            name='provider',
            field=models.ForeignKey(on_delete=models.SET(social.models.get_sentinel_socialprovider), to='social.socialprovider'),
        ),
        migrations.AddConstraint(
            model_name='socialaccount',
            constraint=models.UniqueConstraint(fields=('user', 'provider', 'site'), name='user have one account per provider and site'),
        ),
        migrations.AddConstraint(
            model_name='socialaccount',
            constraint=models.UniqueConstraint(fields=('social_id', 'provider', 'site'), name='every social_id per provider is unique for every site'),
        ),
    ]
