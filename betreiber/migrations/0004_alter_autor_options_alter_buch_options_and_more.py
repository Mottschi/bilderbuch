# Generated by Django 4.1.3 on 2022-11-21 19:48

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('betreiber', '0003_alter_autor_options_alter_mandant_manager'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='autor',
            options={'ordering': ['last_name', 'first_name', 'middle_name'], 'verbose_name_plural': 'Autoren'},
        ),
        migrations.AlterModelOptions(
            name='buch',
            options={'verbose_name_plural': 'Bücher'},
        ),
        migrations.AlterModelOptions(
            name='einladung',
            options={'verbose_name_plural': 'Einladungen'},
        ),
        migrations.AlterModelOptions(
            name='mandant',
            options={'verbose_name_plural': 'Mandanten'},
        ),
        migrations.AlterModelOptions(
            name='seite',
            options={'verbose_name_plural': 'Seiten'},
        ),
        migrations.AlterModelOptions(
            name='sprachaufnahme',
            options={'verbose_name_plural': 'Seiten'},
        ),
        migrations.AlterModelOptions(
            name='sprache',
            options={'verbose_name_plural': 'Sprachen'},
        ),
        migrations.AlterModelOptions(
            name='user',
            options={'ordering': ['username']},
        ),
        migrations.AlterField(
            model_name='mandant',
            name='manager',
            field=models.OneToOneField(on_delete=django.db.models.deletion.RESTRICT, related_name='verwalter', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='user',
            name='mandant',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='member', to='betreiber.mandant'),
        ),
    ]
