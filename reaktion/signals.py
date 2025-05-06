from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from reaktion import models, channel_signals, channels
import logging

logger = logging.getLogger(__name__)
logger.info("Loading signals")


@receiver(post_save, sender=models.RunEvent)
def event_singal(sender, instance=None, **kwargs):
    print("Signal received!")
    if instance:
        print([f"run_{instance.run.id}"])
        channels.run_event_channel.broadcast(channel_signals.RunEventSignal(event=instance.id), [f"run_{instance.run.id}"])
