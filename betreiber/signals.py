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

    if conf_settings.DEBUG:
        thumbnail_file = os.path.join('betreiber', 'static', thumbnail_file)

    if thumbnail_file and os.path.exists(thumbnail_file):
        print('deleting', thumbnail_file)
        os.remove(thumbnail_file)


def handleSeiteBildDeletion():
    pass