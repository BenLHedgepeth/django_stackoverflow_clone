from django.contrib import admin

from .models import Tag

# Register your models here.
class TagAdmin(admin.ModelAdmin):
    fieldset = [(
        "Tags", {
            'fields': ('name')
        }
    )]


admin.site.register(Tag, TagAdmin)
