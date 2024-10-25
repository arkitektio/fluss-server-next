import strawberry
from reaktion import models, enums
from typing import Optional
from strawberry_django.filters import FilterLookup
import strawberry_django


@strawberry.input
class SearchFilter:
    search: Optional[str] | None

    def filter_search(self, queryset, info):
        if self.search is None:
            return queryset
        return queryset.filter(name__icontains=self.search)


@strawberry_django.filter(models.Workspace)
class WorkspaceFilter:
    name: Optional[FilterLookup[str]] | None
    ids: list[strawberry.ID] | None
    search: str | None

    def filter_ids(self, queryset, info):
        if self.ids is None:
            return queryset
        return queryset.filter(id__in=self.ids)
    
    def filter_search(self, queryset, info):
        if self.search is None:
            return queryset
        return queryset.filter(name__icontains=self.search)
    


@strawberry_django.order(models.Workspace)
class WorkspaceOrder:
    created_at: strawberry.auto

@strawberry_django.filter(models.Run)
class RunOrder:
    created_at: strawberry.auto







    

@strawberry_django.filter(models.Run)
class RunFilter:
    ids: list[strawberry.ID] | None
    search: str | None

    def filter_ids(self, queryset, info):
        if self.ids is None:
            return queryset
        return queryset.filter(id__in=self.ids)
    
    def filter_search(self, queryset, info):
        if self.search is None:
            return queryset
        return queryset.filter(flow__name__icontains=self.search)


@strawberry_django.filter(models.Flow)
class FlowFilter:
    workspace: WorkspaceFilter | None
    ids: list[strawberry.ID] | None
    search: str | None

    def filter_ids(self, queryset, info):
        if self.ids is None:
            return queryset
        return queryset.filter(id__in=self.ids)
    
    def filter_search(self, queryset, info):
        if self.search is None:
            return queryset
        return queryset.filter(name__icontains=self.search)


@strawberry_django.filter(models.ReactiveTemplate)
class ReactiveTemplateFilter:
    ids: list[strawberry.ID] | None
    implementations: list[enums.ReactiveImplementation] | None
    search: str | None

    def filter_ids(self, queryset, info):
        if self.ids is None:
            return queryset
        return queryset.filter(id__in=self.ids)

    def filter_implementations(self, queryset, info):
        if self.implementations is None:
            return queryset
        return queryset.filter(implementation__in=self.implementations)
    
    def filter_search(self, queryset, info):
        if self.search is None:
            return queryset
        return queryset.filter(name__icontains=self.search)

