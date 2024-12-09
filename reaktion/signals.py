from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from reaktion import models
from reaktion.channels import runevent_created_broadcast
import logging
from guardian.shortcuts import assign_perm

logger = logging.getLogger(__name__)
logger.info("Loading signals")


@receiver(post_save, sender=models.RunEvent)
def event_singal(sender, instance=None, **kwargs):
    print("Signal received!")
    if instance:
        print([f"run_{instance.run.id}"])
        runevent_created_broadcast(instance.id, [f"run_{instance.run.id}"])
