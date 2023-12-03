"""
Docstring
"""

# Python imports
import os
import json
import urllib.parse
import jwt

# Django imports
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseServerError
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse

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
    app_id = os.getenv( "APP_ID" )
    redirect_url = 'https://' + request.host + '/redirect-wix'
    redirect_url = urllib.parse.quote( redirect_url, safe='~')
    token = request.args.get( 'token' )
    url = permission_request_url + '?token=' + token + '&state=start'
    url += '&appId=' + app_id + '&redirectUrl=' + redirect_url

    print( "redirecting to " + url )
    print( "=============================" )

    # Redirect to the app installation URL.
    return redirect( url )

# Redirect URL (App Authorized, Complete Installation).
def redirect_wix( request ):

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
    authorization_code = request.args.get( 'code' )

    try:
        print( "Getting Tokens From Wix." )
        print( "=======================" )

        # Get a refresh token from Wix.
        refresh_token = json.loads(
            logic.get_tokens_from_wix(
                request,
                authorization_code,
                auth_provider_base_url =os.getenv( 'AUTH_PROVIDER_BASE_URL' ),
                app_secret = os.getenv( 'APP_SECRET' ),
                app_id = os.getenv( 'APP_ID' )
            )
        )[ 'refresh_token' ]

        # Get an access token from Wix.
        access_token = logic.get_access_token(
            request,
            refresh_token,
            auth_provider_base_url = os.getenv( 'AUTH_PROVIDER_BASE_URL' ),
            app_secret = os.getenv( 'APP_SECRET' ),
            app_id = os.getenv( 'APP_ID' )
        )

        # Get data about the installation of this app on the user's website.
        app_instance = logic.get_app_instance(
            request,
            refresh_token,
            'https://www.wixapis.com/apps/v1/instance',
            auth_provider_base_url = os.getenv( 'AUTH_PROVIDER_BASE_URL' ),
            app_secret = os.getenv( 'APP_SECRET' ),
            app_id = os.getenv( 'APP_ID' )
        )

        # Construct the URL to Completes the OAuth flow.
        # https://dev.wix.com/api/rest/getting-started/authentication#getting-started_authentication_step-5a-app-completes-the-oauth-flow
        redirect_url = "https://www.wix.com/installer/close-window?access_token="
        redirect_url += access_token

        # Extract data from the app instance.
        instance_id = app_instance[ 'instance' ][ 'instanceId' ]
        site_id = app_instance[ 'site' ][ 'siteId' ]
        is_free = app_instance[ 'instance' ][ 'isFree' ]

        # Search the User table for the instance ID (primary key)
        #Question.objects.filter(pub_date__lte=timezone.now())
        #selected_choice = question.choice_set.get(pk=request.POST["choice"])
        user_in_db = get_object_or_404(User, pk=instance_id)

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

        # Close the consent window by redirecting the user to the following URL
        # with the user's access token.
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect( reverse( redirect_url ) )

    except ValueError as err:
        print( "Error getting token from Wix" )
        print( err )
        return HttpResponseServerError( "{'error':'wixError'}" )

# Remove application files and data for the user (App Uninstalled)
def uninstall( request ):

    """
    Take action when the application recieves a POST request from the App Removed webhook.
    
    See documentation:
    https://dev.wix.com/docs/rest/api-reference/app-management/apps/app-instance/instance-app-installed
    """

    # Initialize variables.
    instance_id = ''
    secret = os.getenv( 'WEBHOOK_PUBLIC_KEY' )

    # If the user submitted a POST request...
    if request.method == 'POST':

        # Get the encoded data received.
        encoded_jwt = request.data

        # Decode the data using our secret.
        data = jwt.decode( encoded_jwt, secret, algorithms=["RS256"] )

        # Load the JSON payload.
        request_data = json.loads( data['data'] )

        # Print the data received to the console for debugging.
        logic.dump( request_data, "request_data" )

        # Extract the instance ID
        instance_id = request_data[ 'instanceId' ]

        # Search the tables for records, filtering by instance ID.
        user = get_object_or_404( User, pk=instance_id )
        extensions = Extension.objects.filter( instance_id = instance_id )

        # question = get_object_or_404(Question, pk=question_id)
        # selected_choice = question.choice_set.get(pk=request.POST["choice"])

        if user:

            # Delete the user.
            user.delete()

            # Return feedback to the console.
            print( "Deleted user #" + instance_id )

        for extension in extensions:

            # Delete the user.
            extension.delete()

            # Return feedback to the console.
            print( "Deleted component #" + extension.extension_id )

        # Return feedback to the console.
        print( "Instance #" + instance_id + " uninstalled." )

    # The app must return a 200 response upon successful receipt of a webhook.
    # Source: https://dev.wix.com/docs/rest/articles/getting-started/webhooks
    return HttpResponse( status=200 )
