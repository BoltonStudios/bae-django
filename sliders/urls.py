"""
Docstring
"""

# Django imports
from django.urls import path

# Local imports
from . import views

# Define variables
app_name = "sliders"
urlpatterns = [
    path("", views.root, name="index"),
    path("app-wix/", views.app_wix, name="app_wix"),
    path("redirect-wix/", views.redirect_wix, name="redirect_wix"),
    path("uninstall/", views.uninstall, name="uninstall"),
    path("upgrade/", views.upgrade, name="upgrade"),
    path("downgrade/", views.downgrade, name="downgrade"),
    path("settings/", views.settings, name="settings"),
    path("widget/", views.widget, name="widget"),
]
