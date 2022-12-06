from django.db.models.signals import pre_delete, post_delete
from django.dispatch import receiver

import os

from .models import Buch, Seite, Sprachaufnahme
from django.conf import settings as conf_settings

@receiver(post_delete, sender=Buch)
def post_delete_buch(sender, **kwargs):
    '''
    handles cleanup actions that need to be done after a book is deleted
    '''
    instance = kwargs['instance']
    thumbnail_file = instance.thumbnail

    if conf_settings.RENDER:
        thumbnail_file = os.path.join(conf_settings.PERSISTENT_STORAGE_ROOT, 'static', thumbnail_file)
    else:
        thumbnail_file = os.path.join('betreiber', 'static', thumbnail_file)

    if thumbnail_file and os.path.exists(thumbnail_file):
        os.remove(thumbnail_file)

@receiver(post_delete, sender=Seite)
def handleSeiteBildDeletion(sender, **kwargs):
    '''
    handles cleanup actions that need to be done after a page is deleted
    '''
    instance = kwargs['instance']
    picture = instance.picture

    if conf_settings.RENDER:
        picture = os.path.join(conf_settings.PERSISTENT_STORAGE_ROOT, 'static', picture)
    else:
        picture = os.path.join('betreiber', 'static', picture)

    if picture and os.path.exists(picture):
        os.remove(picture)
    else:
        print('no file for this page found')

@receiver(post_delete, sender=Sprachaufnahme)
def post_delete_sprachaufnahme(sender, **kwargs):
    '''
    handles cleanup actions that need to be done after a recording is deleted
    '''
    instance = kwargs['instance']
    audio_file = instance.audio

    if conf_settings.RENDER:
        audio_file = os.path.join(conf_settings.PERSISTENT_STORAGE_ROOT, 'static', audio_file)
    else:
        audio_file = os.path.join('endnutzer', 'static', audio_file)

    if audio_file and os.path.exists(audio_file):
        os.remove(audio_file)