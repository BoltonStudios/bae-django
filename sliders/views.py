"""
Docstring
"""

# Python imports
import json
import urllib.parse
import jwt

# Django imports
from django.http import HttpResponse, HttpResponseServerError
from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings as conf_settings
from django.templatetags.static import static

# Local imports.
from .models import User, Extension
from . import logic

# Create your views here.

# Homepage.
def root( request ):

    """Return a friendly greeting."""

    # Initialize variables.
    message = "The app is running."

    # Redisplay the question voting form.
    return render(
        request,
        "sliders/index.html",
        {
            "message": message,
        },
    )

# App URL (Installation) page.
def app_wix( request ):

    """
    The program calls this route before Wix asks the user to provide consent.

    Configure the 'App URL' in the Wix Developers to point here
    This code was adapted from functions posted by SAMobileDev repository here: 
    https://github.com/wix-incubator/sample-wix-rest-app/blob/master/src/index.js
    Source: Wix Sample Rest App source code https://github.com/wix-incubator
    retrieved in June 2023.
    """

    print( "Got a call from Wix for app installation." )
    print( "==============================" )

    # Construct the app installation URL.
    permission_request_url = "https://www.wix.com/installer/install"
    app_id = conf_settings.APP_ID
    redirect_url = 'https://' + request.META[ 'HTTP_HOST' ] + '/sliders/redirect-wix/'
    redirect_url = urllib.parse.quote( redirect_url, safe='~')
    token = request.GET[ 'token' ]
    url = permission_request_url + '?token=' + token + '&state=start'
    url += '&appId=' + app_id + '&redirectUrl=' + redirect_url

    print( "redirecting to " + url )
    print( "=============================" )

    # Redirect to the app installation URL.
    return redirect( url )

# Redirect URL (App Authorized, Complete Installation).
def redirect_wix( request ):

    # pylint: disable=too-many-locals
    # pylint: disable=too-many-statements
    # Our variables are reasonable in this case.
    """
    The program calls this route once the user finishes installing your application 
    and Wix redirects them to your application's site (here).

    Configure the 'Redirect URL' in Wix Developers to point here.
    This code was adapted from functions posted by SAMobileDev repository here: 
    https://github.com/wix-incubator/sample-wix-rest-app/blob/master/src/index.js
    Source: Wix Sample Rest App source code https://github.com/wix-incubator
    retrieved in June 2023.
    """
    print( "Got a call from Wix for redirect-wix." )
    print( "=============================" )

    # Get the authorization code from Wix.
    authorization_code = request.GET.get( 'code' )

    try:
        print( "Getting Tokens From Wix." )
        print( "=======================" )

        auth_provider_base_url = conf_settings.AUTH_PROVIDER_BASE_URL
        app_secret = conf_settings.APP_SECRET
        app_id = conf_settings.APP_ID

        # Get a refresh token from Wix.
        refresh_token = json.loads(
            logic.get_tokens_from_wix(
                authorization_code,
                auth_provider_base_url,
                app_secret,
                app_id
            )
        )[ 'refresh_token' ]

        # Get an access token from Wix.
        access_token = logic.get_access_token(
            refresh_token,
            auth_provider_base_url,
            app_secret,
            app_id
        )

        # Get data about the installation of this app on the user's website.
        app_instance = logic.get_app_instance(
            refresh_token,
            'https://www.wixapis.com/apps/v1/instance',
            auth_provider_base_url,
            app_secret,
            app_id
        )

        # Construct the URL to Completes the OAuth flow.
        # https://dev.wix.com/api/rest/getting-started/authentication#getting-started_authentication_step-5a-app-completes-the-oauth-flow
        complete_oauth_redirect_url = "https://www.wix.com/installer/close-window?access_token="
        complete_oauth_redirect_url += access_token

        # Extract data from the app instance.
        instance_id = app_instance[ 'instance' ][ 'instanceId' ]
        site_id = app_instance[ 'site' ][ 'siteId' ]
        is_free = app_instance[ 'instance' ][ 'isFree' ]

        # Search the User table for the instance ID (primary key)
        #Question.objects.filter(pub_date__lte=timezone.now())
        #selected_choice = question.choice_set.get(pk=request.POST["choice"])
        user_in_db = User.objects.filter( pk=instance_id ).first()

        # If the user does not exist in the table...
        if user_in_db is None:

            # Construct a new User record.
            user = User(
                instance_id = app_instance[ 'instance' ][ 'instanceId' ],
                site_id = app_instance[ 'site' ][ 'siteId' ],
                is_free = app_instance[ 'instance' ][ 'isFree' ],
                refresh_token = refresh_token
            )

        else:

            # Update the user record.
            user = user_in_db
            user.site_id = site_id
            user.is_free = is_free
            user.refresh_token = refresh_token

        # Add the new or updated user record to the User table.
        user.save()

        # Mark the installation complete.
        installation_complete_response = logic.finish_app_installation( access_token )

        logic.dump( installation_complete_response, 'installation_complete_response' )

        # Close the consent window by redirecting the user to the following URL
        # with the user's access token.
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.

        print( "redirecting to " + complete_oauth_redirect_url )
        print( "=============================" )

        return redirect( complete_oauth_redirect_url, permanent=True )

    except ValueError as err:
        print( "Error getting token from Wix" )
        print( err )
        return HttpResponseServerError( "{'error':'wixError'}" )

# Remove application files and data for the user (App Uninstalled)
@method_decorator( csrf_exempt )
def uninstall( request ):

    """
    Take action when the application recieves a POST request from the App Removed webhook.
    
    See documentation:
    https://dev.wix.com/docs/rest/api-reference/app-management/apps/app-instance/instance-app-installed
    """

    # Initialize variables.
    instance_id = ''
    secret = conf_settings.WEBHOOK_PUBLIC_KEY

    # If the user submitted a POST request...
    if request.method == 'POST':

        # Get the encoded data received.
        encoded_jwt = request.body

        # Decode the data using our secret.
        data = jwt.decode( encoded_jwt, secret, algorithms=["RS256"] )

        # Load the JSON payload.
        request_data = json.loads( data['data'] )

        # Extract the instance ID
        instance_id = request_data[ 'instanceId' ]

        # Search the tables for records, filtering by instance ID.
        user = get_object_or_404( User, pk=instance_id )
        extensions = Extension.objects.filter( instance_id = instance_id )

        if user:

            # Delete the user.
            user.delete()

            # Return feedback to the console.
            print( "Deleted user #" + instance_id )

        for extension in extensions:

            # Delete the user.
            extension.delete()

            # Return feedback to the console.
            print( "Deleted extension #" + extension.extension_id )

        # Return feedback to the console.
        print( "Instance #" + instance_id + " uninstalled." )

    # The app must return a 200 response upon successful receipt of a webhook.
    # Source: https://dev.wix.com/docs/rest/articles/getting-started/webhooks
    return HttpResponse( status=200 )

# App Settings Panel
@method_decorator( csrf_exempt )
def settings( request ):

    # pylint: disable=too-many-locals
    # pylint: disable=too-many-statements
    # Our variables are reasonable in this case.

    """
    Build the App Settings panel allowing users to customize the app iframe extension.
    
    Find recommended App Settings panel features here:
    https://devforum.wix.com/kb/en/article/build-an-app-settings-panel-for-website-iframe-components
    """

    print("Settings route called.")

    # Initialize variables.
    instance_id = None
    requested_extension_id = None
    extension_in_db = None
    before_image = static('sliders/images/placeholder-1.svg')
    before_label_text = 'Before'
    before_alt_text = ''
    after_image = static('sliders/images/placeholder-3.svg')
    after_label_text = 'After'
    after_alt_text = ''
    slider_offset = 50
    slider_offset_float = 0.5
    is_overlay_enabled = True
    is_move_on_click_enabled = False
    is_vertical = False
    is_free = False # False for dev environmet. Change to True for production.

    # If the user submitted a GET request...
    if request.method == 'GET':
        
        #
        if 'origCompId' in request.GET.keys() :

            # Assign the value of 'origCompId' from the GET request to the extension_id variable.
            requested_extension_id = request.GET[ 'origCompId' ]

            # Search the Extension table for the extension by its extension ID (primary key).
            extension_in_db = Extension.objects.filter( pk=requested_extension_id ).first()

            # Load existing extension...
            if extension_in_db is not None:

                # Update the local variables with the requested_extension values.
                instance_id                 = extension_in_db.instance_id
                before_image                = extension_in_db.before_image
                before_label_text           = extension_in_db.before_label_text
                before_alt_text             = extension_in_db.before_alt_text
                after_image                 = extension_in_db.after_image
                after_label_text            = extension_in_db.after_label_text
                after_alt_text              = extension_in_db.after_alt_text
                slider_offset               = extension_in_db.offset
                slider_offset_float         = extension_in_db.offset_float
                is_overlay_enabled          = extension_in_db.is_overlay_enabled
                is_move_on_click_enabled    = extension_in_db.is_move_on_click_enabled
                is_vertical                 = extension_in_db.is_vertical

    # Pass local variables to Django and render the template.
    return render(
        request,
        "sliders/settings.html",
        {
            "page_id": "settings",
            "instance_id": instance_id,
            "is_free": is_free,
            "extension_id": requested_extension_id,
            "before_image": before_image,
            "before_label_text": before_label_text,
            "before_alt_text": before_alt_text,
            "after_image": after_image,
            "after_label_text": after_label_text,
            "after_alt_text": after_alt_text,
            "slider_offset": slider_offset,
            "slider_offset_float": slider_offset_float,
            "is_vertical": is_vertical,
            "is_overlay_enabled": is_overlay_enabled,
            "is_move_on_click_enabled": is_move_on_click_enabled
        },
    )

# Widget Extension
@method_decorator( csrf_exempt )
def widget( request ):

    # pylint: disable=too-many-locals
    # pylint: disable=too-many-statements
    # Our variables are reasonable in this case.

    """
    Build the widget iframe extension containing a before-and-after slider.
    """

    # Initialize variables.
    requested_extension_id = None
    extension_in_db = None
    before_image = static('sliders/images/placeholder-1.svg')
    before_label_text = 'Before'
    before_alt_text = ''
    after_image = static('sliders/images/placeholder-3.svg')
    after_label_text = 'After'
    after_alt_text = ''
    slider_offset = 50
    slider_offset_float = 0.5
    slider_orientation = 'horizontal'
    is_vertical = False
    is_overlay_enabled = True
    is_move_on_click_enabled = False

    # If the user submitted a POST request...
    if request.method == 'POST':

        # Get the data received.
        request_data = json.loads( request.body )
        requested_extension_id = request_data[ "extensionID" ]
        logic.dump( request_data, 'request_data')

        # Search the extensionSlider table for the extension by its extension ID (primary key).
        extension_in_db = Extension.objects.filter( pk=requested_extension_id ).first()

        # Edit existing extension.
        if extension_in_db is not None:

            # Delete existing extension.
            if request_data[ "action" ] == "delete" :

                # Delete the extension by its ID.
                extension_in_db.delete()

            else:

                # If the user selected the vertical orientation...
                if request_data[ 'sliderOrientation' ] == 'vertical' :

                    # Update the variable.
                    is_vertical = True

                # Edit the extensionSlider record.
                extension_in_db.before_image = request_data[ 'beforeImage' ]
                extension_in_db.before_label_text = request_data[ 'beforeLabelText' ]
                extension_in_db.before_alt_text = request_data[ 'beforeAltText' ]
                extension_in_db.after_image = request_data[ 'afterImage' ]
                extension_in_db.after_label_text = request_data[ 'afterLabelText' ]
                extension_in_db.after_alt_text = request_data[ 'afterAltText' ]
                extension_in_db.offset = request_data[ 'sliderOffset' ]
                extension_in_db.offset_float = request_data[ 'sliderOffsetFloat' ]
                extension_in_db.is_vertical = is_vertical
                extension_in_db.is_overlay_enabled = request_data[ 'sliderMouseoverAction' ]
                extension_in_db.is_move_on_click_enabled = request_data[ 'sliderMoveOnClickToggle' ]

                # Add a new extension to the Extension table.
                extension_in_db.save()

        else:

            # Create new extension.

            # If the request contains an instance ID...
            if 'instanceID' in request_data.keys():

                # Get the associated User instance.
                user_in_db = User.objects.filter( pk=request_data[ 'instanceID' ] ).first()

                # If the user selected the vertical orientation...
                if request_data[ 'sliderOrientation' ] == 'vertical' :

                    # Update the variable.
                    is_vertical = True

                # Construct a new Extension record.
                extension = Extension(
                    extension_id = requested_extension_id,
                    instance_id = user_in_db,
                    before_image = request_data[ 'beforeImage' ],
                    before_label_text = request_data[ 'beforeLabelText' ],
                    before_alt_text = request_data[ 'beforeAltText' ],
                    after_image = request_data[ 'afterImage' ],
                    after_label_text = request_data[ 'afterLabelText' ],
                    after_alt_text = request_data[ 'afterAltText' ],
                    offset = request_data[ 'sliderOffset' ],
                    offset_float = request_data[ 'sliderOffsetFloat' ],
                    is_vertical = is_vertical,
                    is_overlay_enabled = request_data[ 'sliderMouseoverAction' ],
                    is_move_on_click_enabled = request_data[ 'sliderMoveOnClickToggle' ]
                )

                # Add a new extension to the extensionSlider table.
                extension.save()

        # Return a success message.
        return HttpResponse(status=201)

    # If the user submitted a GET request...
    if request.method == 'GET':

        # If the GET request provided the 'origCompId'...
        if 'origCompId' in request.GET.keys() :

            # Assign its value to extension_id...
            requested_extension_id = request.GET[ 'origCompId' ]

        elif 'viewerCompId' in request.GET.keys() :

            # Otherwise, use the 'viewerCompId' (front-end) extension ID.
            requested_extension_id = request.GET[ 'viewerCompId' ]

        # Search the database and get the extension by the requested extension ID (primary key).
        extension_in_db = Extension.objects.filter( pk=requested_extension_id ).first()

        # Extension found.
        if extension_in_db is not None:

            # If the user selected the vertical orientation...
            if extension_in_db.is_vertical is True :

                # Update the local variable for use in the widget template.
                slider_orientation  = 'vertical'

            # Update the local variables.
            before_image = extension_in_db.before_image
            before_label_text = extension_in_db.before_label_text
            before_alt_text = extension_in_db.before_alt_text
            after_image = extension_in_db.after_image
            after_label_text = extension_in_db.after_label_text
            after_alt_text = extension_in_db.after_alt_text
            slider_offset = extension_in_db.offset
            slider_offset_float = extension_in_db.offset_float
            is_overlay_enabled = extension_in_db.is_overlay_enabled
            is_move_on_click_enabled = extension_in_db.is_move_on_click_enabled

    # Pass local variables to Django and render the template.
    print( "int( is_overlay_enabled ) is ")
    print( int( is_overlay_enabled ) )
    return render(
        request,
        "sliders/widget.html",
        {
            "page_id": "widget",
            "extension_id": requested_extension_id,
            "before_image": before_image,
            "before_label_text": before_label_text,
            "before_alt_text": before_alt_text,
            "after_image": after_image,
            "after_label_text": after_label_text,
            "after_alt_text": after_alt_text,
            "slider_offset": slider_offset,
            "slider_offset_float": slider_offset_float,
            "slider_orientation": slider_orientation,
            "slider_mouseover_action": int( is_overlay_enabled ),
            "slider_move_on_click_toggle": int( is_move_on_click_enabled )
        }
    )
