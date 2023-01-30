import logging

from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver

logger = logging.getLogger(__name__)

@receiver(user_logged_in)
def on_login(sender, user, request, **kwargs):
    logger.info(f'Пользователь {user.username} зашёл на сайт')