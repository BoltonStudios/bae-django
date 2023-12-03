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
    instance_id     = models.CharField( primary_key=True, max_length=200 )
    site_id         = models.CharField( unique=True, max_length=200 )
    user_id         = models.CharField( unique=True, max_length=200 )
    refresh_token   = models.CharField( unique=True, max_length=200 )
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
    extension_id        = models.CharField( primary_key=True, max_length=200 )
    instance_id         = models.ForeignKey( User, on_delete=models.CASCADE )
    before_image        = models.CharField( max_length=1000 )
    before_label_text   = models.CharField( max_length=1000 )
    before_alt_text     = models.CharField( max_length=1000 )
    after_image         = models.CharField( max_length=1000 )
    after_label_text    = models.CharField( max_length=1000 )
    after_alt_text      = models.CharField( max_length=1000 )
    offset              = models.IntegerField()
    offset_float        = models.FloatField()
    is_vertical         = models.BooleanField()
    created             = models.DateTimeField( auto_now_add=True )
    last_modified       = models.DateTimeField( auto_now=True )

    def __str__( self ):
        return f'<slider { self.extension_id } in { self.instance_id }>'
