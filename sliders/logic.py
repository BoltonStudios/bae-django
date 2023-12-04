'''
Helper functions mostly to handle Wix authorization.
'''
# pylint: disable=broad-exception-caught

# Import dependencies.
import requests

# Dump variable values to the terminal.
def dump( item, name ):
    '''
    Print the item contents to the terminal.
    '''
    print( type( item ) )
    print( name + "=" )
    print( item )
    print( "===========================" )

# Define functions.
def get_tokens_from_wix( auth_code, auth_provider_base_url, app_secret, app_id ):

    """
    Request an Access Token from Wix.
    
    This code was adapted from functions posted by SAMobileDev repository here: 
    https://github.com/wix-incubator/sample-wix-rest-app/blob/master/src/index.js
    Source: Wix Sample Rest App source code https://github.com/wix-incubator
    retrieved in June 2023.
    """

    # Initialize variables.
    url = auth_provider_base_url + "/access"
    body_parameters = {
        'code': auth_code,
        'client_secret': app_secret,
        'client_id': app_id,
        'grant_type': "authorization_code"
    }

    # Request an access token.
    token_request = requests.post( url, json = body_parameters, timeout=2.50 )

    # Extract the access token.
    access_token = token_request.text

    # Return the access token.
    return access_token

def get_access_token( refresh_token, auth_provider_base_url, app_secret, app_id ):

    """
    Get a new Wix Access Token using a Refresh Token.
    
    This code was adapted from functions posted by SAMobileDev repository here: 
    https://github.com/wix-incubator/sample-wix-rest-app/blob/master/src/index.js
    Source: Wix Sample Rest App source code https://github.com/wix-incubator
    retrieved in June 2023.
    """

    # Initialize variables.
    url = auth_provider_base_url + "/access"
    body_parameters = {
        'refresh_token': refresh_token,
        'client_secret': app_secret,
        'client_id': app_id,
        'grant_type': "refresh_token"
    }

    # Request an access token.
    token_request = requests.post( url, json = body_parameters, timeout = 2.50 ).json()

    # Extract the access token from response.
    access_token = token_request[ 'access_token' ]

    # Return the access token.
    return access_token

def get_app_instance( refresh_token, instance_api_url, auth_provider_base_url, app_secret, app_id ):

    """
    This is sample call to Wix instance API - you can find it here: 
    https://dev.wix.com/api/rest/app-management/apps/app-instance/get-app-instance
    """

    try:
        print( 'getAppInstance with refreshToken = ' + refresh_token )
        print( "==============================" )
        access_token = get_access_token( refresh_token, auth_provider_base_url, app_secret, app_id )

        headers = {
            'Authorization': access_token
        }
        instance = requests.get( instance_api_url, headers = headers, timeout = 2.50 ).json()

        return instance

    except Exception as err :

        # Provide feedback for the user.
        print( 'error in getAppInstance' )
        print( err )

        # Exit the function.
        return err
