import uuid

from authentikate import App
from django.contrib.auth import get_user_model

# Create your models here.
from django.db import models

# Create your models here.
from django_choices_field import TextChoicesField

from . import enums


class Room(models.Model):
    """Room is a Template for a Template"""

    restrict = models.JSONField(
        default=list,
        help_text="Restrict access to specific nodes for this diagram okay?",
    )
    title = models.CharField(max_length=10000, null=True)
    description = models.CharField(max_length=10000, null=True)
    creator = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, null=True, blank=True
    )
    pinned_by = models.ManyToManyField(
        get_user_model(),
        related_name="pinned_workspaces",
        blank=True,
        help_text="The users that have pinned the workspace",
    )

    def __str__(self):
        return f"{self.title}"


class Agent(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    name = models.CharField(max_length=10000, null=True)
    app = models.ForeignKey(App, max_length=4000)
    user = models.ForeignKey(User, max_length=4000)


class Portal(models.Model):
    """A portal is a media outlet

    that allows to permamently attach media to a room
    a port can be pinned by users to appear in close
    proximity

    """

    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    causing_agent = models.ForeignKey("Agent", on_delete=models.CASCADE)
    open = models.BooleanField(default=True, help_text="Is the portal still open")


class StreamPortal(models.Model):
    pass


class Structure(models.Model):
    identifier = models.CharField(max_length=3000)
    object = models.CharField(max_length=6000)


class Message(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE)
    is_streaming = models.BooleanField(
        default=False,
        help_text="Is the message currently streaming? Will mark it as streaming on the webinterface",
    )
    attached_structures = models.ManyToManyField(
        Structure, help_text="Does this message "
    )
