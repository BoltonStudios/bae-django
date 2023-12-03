"""
Docstring
"""

# Django imports
from django.contrib import admin

# Local imports
from .models import User, Extension

# Register your models here.
admin.site.register( User )
admin.site.register( Extension )
