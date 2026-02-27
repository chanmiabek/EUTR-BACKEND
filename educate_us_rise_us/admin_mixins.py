from django.db import models
from django_summernote.widgets import SummernoteWidget


class RichTextAdminMixin:
    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if isinstance(db_field, models.TextField):
            kwargs["widget"] = SummernoteWidget()
        return super().formfield_for_dbfield(db_field, request, **kwargs)
