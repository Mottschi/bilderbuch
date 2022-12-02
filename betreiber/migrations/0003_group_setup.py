# Generated by Django 4.1.3 on 2022-11-28 18:04

from django.db import migrations

from django.contrib.auth.models import Group

def create_groups(apps, schema_editor):
    Group.objects.create(name='systemadmin')
    Group.objects.create(name='betreiber')
    Group.objects.create(name='endnutzer')

class Migration(migrations.Migration):

    dependencies = [
        ('betreiber', '0002_language_setup'),
    ]

    operations = [
        migrations.RunPython(create_groups)
    ]