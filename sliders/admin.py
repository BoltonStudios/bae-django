"""
Docstring
"""

# Django imports
from django.contrib import admin

# Local imports
from .models import User, Extension

class ExtensionInline(admin.TabularInline):
    model = Extension
    extra = 0

class UserAdmin(admin.ModelAdmin):
    inlines = [ExtensionInline]

# Register your models here.
admin.site.register( User, UserAdmin )
admin.site.register( Extension )
