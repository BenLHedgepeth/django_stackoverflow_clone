from django.contrib import admin

from .models import UserAccount
# Register your models here.

class UserAccountAdmin(admin.ModelAdmin):
    fields = ("user", )


admin.site.register(UserAccount, UserAccountAdmin)
