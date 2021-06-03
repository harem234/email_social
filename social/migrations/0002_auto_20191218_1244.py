# Generated by Django 2.2.8 on 2019-12-18 09:14

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


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
            model_name='socialaccount',
            constraint=models.UniqueConstraint(fields=('user', 'provider', 'site'), name='user have one account per provider and site'),
        ),
        migrations.AddConstraint(
            model_name='socialaccount',
            constraint=models.UniqueConstraint(fields=('social_id', 'provider', 'site'), name='every social_id per provider is unique for every site'),
        ),
    ]