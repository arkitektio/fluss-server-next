import uuid

from django.contrib.auth import get_user_model

# Create your models here.
from django.db import models

# Create your models here.
from django_choices_field import TextChoicesField

from . import enums


class Workspace(models.Model):
    """Graph is a Template for a Template"""

    restrict = models.JSONField(
        default=list,
        help_text="Restrict access to specific nodes for this diagram okay?",
    )
    title = models.CharField(max_length=10000, null=True)
    description = models.CharField(max_length=10000, null=True)
    creator = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_created=True, auto_now_add=True)
    pinned_by = models.ManyToManyField(
        get_user_model(),
        related_name="pinned_workspaces",
        blank=True,
        help_text="The users that have pinned the workspace",
    )

    def __str__(self):
        return f"{self.title}"


class Flow(models.Model):
    workspace = models.ForeignKey(
        Workspace, on_delete=models.CASCADE, null=True, blank=True, related_name="flows"
    )
    creator = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, null=True, blank=True
    )
    restrict = models.JSONField(
        default=list, help_text="Restrict access to specific nodes for this diagram"
    )
    version = models.CharField(max_length=100, default="1.0alpha")
    title = models.CharField(max_length=10000, null=True)
    description = models.CharField(max_length=10000, null=True)
    nodes = models.JSONField(null=True, blank=True, default=list)
    edges = models.JSONField(null=True, blank=True, default=list)
    graph = models.JSONField(null=True, blank=True)
    hash = models.CharField(max_length=4000, default=uuid.uuid4)
    description = models.CharField(
        max_length=50000, default="Add a Desssscription", blank=True, null=True
    )
    brittle = models.BooleanField(
        default=False,
        help_text="Is this a brittle flow? aka. should the flow fail on any exception?",
    )
    pinned_by = models.ManyToManyField(
        get_user_model(),
        related_name="pinned_flows",
        blank=True,
        help_text="The users that have pinned the position",
    )
    created_at = models.DateTimeField(auto_created=True, auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["workspace", "hash"],
                name="Equal Reservation on this App by this Waiter is already in place",
            )
        ]


class ReactiveTemplate(models.Model):
    title = models.CharField(max_length=100, null=True, blank=True)
    description = models.CharField(max_length=1000, null=True, blank=True)
    implementation = TextChoicesField(
        max_length=1000,
        choices_enum=enums.ReactiveImplementationChoices,
        default=enums.ReactiveImplementationChoices.ZIP.value,
        help_text="Check async Programming Textbook",
    )
    ins = models.JSONField(null=True, blank=True, default=list)
    outs = models.JSONField(null=True, blank=True, default=list)
    voids = models.JSONField(null=True, blank=True, default=list)
    constants = models.JSONField(null=True, blank=True, default=list)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["title", "description"],
                name="Only one Reactive Template with this title and description",
            )
        ]


# Montoring Classes
class Run(models.Model):
    flow = models.ForeignKey(
        Flow, on_delete=models.CASCADE, null=True, blank=True, related_name="runs"
    )

    assignation = models.CharField(null=True, blank=True, max_length=1000)
    status = models.CharField(max_length=100, default="RUNNING")
    snapshot_interval = models.IntegerField(null=True, blank=True)
    pinned_by = models.ManyToManyField(
        get_user_model(),
        related_name="pinned_runs",
        blank=True,
        help_text="The users that have pinned the position",
    )
    created_at = models.DateTimeField(auto_created=True, auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.flow.workspace.name} - {self.assignation}"


class Snapshot(models.Model):
    run = models.ForeignKey(
        Run, on_delete=models.CASCADE, null=True, blank=True, related_name="snapshots"
    )
    t = models.IntegerField()
    status = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_created=True, auto_now_add=True)


class RunEvent(models.Model):
    reference = models.CharField(max_length=1000, null=True, blank=True)
    run = models.ForeignKey(
        Run, on_delete=models.CASCADE, null=True, blank=True, related_name="events"
    )
    snapshot = models.ManyToManyField(Snapshot, related_name="events")
    kind = TextChoicesField(
        max_length=1000,
        choices_enum=enums.RunEventKindChoices,
        default=enums.RunEventKindChoices.NEXT.value,
        help_text="The type of event",
    )
    t = models.IntegerField()
    caused_by = models.JSONField(default=list, blank=True)
    source = models.CharField(max_length=1000)
    handle = models.CharField(max_length=1000, blank=True)
    created_at = models.DateTimeField(auto_created=True, auto_now_add=True)
    value = models.JSONField(null=True, blank=True)
    exception = models.CharField(max_length=2000, blank=True, null=True)

    def __str__(self) -> str:
        return f"Events for {self.run}"


class Trace(models.Model):
    flow = models.ForeignKey(
        Flow, on_delete=models.CASCADE, null=True, blank=True, related_name="traces"
    )
    provision = models.JSONField(null=True, blank=True, max_length=1000)
    snapshot_interval = models.IntegerField(null=True, blank=True)
    pinned_by = models.ManyToManyField(
        get_user_model(),
        related_name="pinned_conditions",
        blank=True,
        help_text="The users that have pinned the position",
    )

    def __str__(self) -> str:
        return f"{self.flow.name} - {self.provision}"


class TraceSnapshot(models.Model):
    trace = models.ForeignKey(
        Trace, on_delete=models.CASCADE, null=True, blank=True, related_name="snapshots"
    )
    status = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_created=True, auto_now_add=True)


class TraceEvent(models.Model):
    trace = models.ForeignKey(
        Trace, on_delete=models.CASCADE, null=True, blank=True, related_name="events"
    )
    snapshot = models.ManyToManyField(TraceSnapshot, related_name="events")
    source = models.CharField(max_length=1000)
    value = models.CharField(max_length=1000, blank=True)
    state = models.CharField(max_length=1000, blank=True)
    created_at = models.DateTimeField(auto_created=True, auto_now_add=True)


from .signals import *
