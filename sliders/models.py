"""
Docstring
"""

# Django imports
from django.db import models

# Define the user model class.
class User( models.Model ):
    """
    Class to define the User table.
    """
    instance_id     = models.CharField( primary_key=True, max_length=255 )
    site_id         = models.CharField( unique=True, max_length=255 )
    refresh_token   = models.TextField()
    is_free         = models.BooleanField()
    created         = models.DateTimeField( auto_now_add=True )
    last_modified   = models.DateTimeField( auto_now=True )

    def __str__( self ):
        return f'<user { self.instance_id }>'

# Define the extension model class.
class Extension( models.Model ):
    """
    Class to define the Extension table.
    """
    extension_id                = models.CharField( primary_key=True, max_length=255 )
    instance_id                 = models.ForeignKey( User, on_delete=models.CASCADE )
    before_image                = models.TextField()
    before_label_text           = models.CharField( max_length=255, blank=True )
    before_alt_text             = models.CharField( max_length=255, blank=True )
    after_image                 = models.TextField()
    after_label_text            = models.CharField( max_length=255, blank=True )
    after_alt_text              = models.CharField( max_length=255, blank=True )
    offset                      = models.IntegerField()
    offset_float                = models.FloatField()
    is_vertical                 = models.BooleanField( default=False )
    mouseover_action            = models.IntegerField( default=1 )
    handle_animation            = models.IntegerField( default=0 )
    is_move_on_click_enabled    = models.BooleanField( default=False )
    created                     = models.DateTimeField( auto_now_add=True )
    last_modified               = models.DateTimeField( auto_now=True )

    def __str__( self ):
        return f'<slider { self.extension_id } in { self.instance_id }>'
