# Generated by Django 2.2.8 on 2019-12-18 09:14

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import social.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('sites', '0002_alter_domain_unique'),
    ]

    operations = [
        migrations.CreateModel(
            name='SocialAccount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('social_id', models.CharField(max_length=1000)),
                ('is_connected', models.BooleanField(default=False)),
                ('email', models.CharField(max_length=1000, null=True, unique=True, validators=[django.core.validators.EmailValidator])),
                ('credentials', models.TextField(max_length=1000, null=True)),
                ('scopes', models.TextField(max_length=1000, null=True)),
            ],
            options={
                'verbose_name': 'Social_Account',
                'verbose_name_plural': 'Social_Accounts',
            },
        ),
        migrations.CreateModel(
            name='SocialProvider',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('social', models.CharField(choices=[(None, 'Select Provider'), ('google', 'Google'), ('github', 'Github'), ('sentinel', 'sentinel')], db_column='social_provider', max_length=10, unique=True)),
                ('client_id', models.CharField(max_length=1000)),
            ],
            options={
                'verbose_name': 'Social_Provider',
                'verbose_name_plural': 'Social_Providers',
            },
        ),
        migrations.AddConstraint(
            model_name='socialprovider',
            constraint=models.UniqueConstraint(fields=('social', 'client_id'), name='every client_id  per social is unique'),
        ),
        migrations.AddField(
            model_name='socialaccount',
            name='provider',
            field=models.ForeignKey(on_delete=models.SET(social.models.get_sentinel_socialprovider), to='social.SocialProvider'),
        ),
        migrations.AddField(
            model_name='socialaccount',
            name='site',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='socialaccount_site', to='sites.Site'),
        ),
    ]
