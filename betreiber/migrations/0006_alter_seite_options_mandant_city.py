# Generated by Django 4.1.3 on 2022-11-24 10:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('betreiber', '0005_alter_mandant_manager_alter_seite_book_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='seite',
            options={'ordering': ['seitenzahl'], 'verbose_name_plural': 'Seiten'},
        ),
        migrations.AddField(
            model_name='mandant',
            name='city',
            field=models.CharField(default='', max_length=30),
        ),
    ]