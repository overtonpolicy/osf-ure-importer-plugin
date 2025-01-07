""" osfflask module for managing Google services 

Copyright (c) 2024, Kevin Crouse. 

This file is part of the *URE Methods Plugin Repository*, located at 
https://github.com/kcphila/osf-ure-plugins

This file is distributed under the terms of the GNU General Public License 3.0
and can be used, shared, or modified provided you attribute the original work 
to the original author, Kevin Crouse.

See the README.md in the root of the project directory, or go to 
http://www.gnu.org/licenses/gpl-3.0.html for license details.
"""
import yaml, json 
import requests 
import flask
import sys
import os 
from . import auth, osf

import oauthlib.oauth2 # just for exceptions
    
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'


bp = flask.Blueprint('google', __name__, url_prefix='/google')


GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"


def get_oauth_details():
    """ This is the client id that is registered in OSF and tied ot the hostname. """
    dev_mode = auth.development_level()

    with open('conf/googleauth.yml') as fh:
        secrets = yaml.load(fh, Loader=yaml.CLoader)

    if dev_mode not in secrets:
        raise Exception(f"Cannot find mode '{dev_mode}' in the OSF Oauth Configuration")
    return(secrets[dev_mode])


@bp.route('/login', methods=('GET', 'POST'))
def googlelogin():
    """ This is the Google login webpage, for testing """
    return(flask.render_template('google/login.html'))


def get_scopes(contexts):
    """ Return a list of Google API scopes based on the context of use. Context is intended to expand as we add more functions
    Args:
        contexts (list|str): a contexts or contexts that indicate the scopes
    """
    if type(contexts) is not list:
        contexts = [contexts]
    
    # start all scopes with basic profile stuff
    scopes = [
        "openid",
        "https://www.googleapis.com/auth/userinfo.profile",
        "https://www.googleapis.com/auth/userinfo.email",
    ]

    for context in contexts:
        if context == 'import':
            scopes.extend(["https://www.googleapis.com/auth/drive.readonly", "https://www.googleapis.com/auth/documents.readonly"])
        else:
            raise Exception(f"We do not recognize a context of {context}")
    return(scopes)

@bp.route('/authenticate', methods=('GET', 'POST'))
def googleauthenticate():
    """ This is the webpage for the Google authentication window. This is expected to be called in a popup. """

    # Find out what URL to hit for Google login
    secrets = get_oauth_details()
    scopes = ' '.join(get_scopes('import'))

    # Use the client_secret.json file to identify the application requesting
    # authorization. The client ID (from that file) and access scopes are required.
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        'conf/google_client_secret.json',
        scopes=scopes,
    )

    # add the redirect url
    flow.redirect_uri = secrets['url']

    # Generate URL for request to Google's OAuth 2.0 server.
    authorization_url, state = flow.authorization_url(
        # Enable offline access so that you can refresh an access token without
        # re-prompting the user for permission. Recommended for web server apps.
        access_type='offline',
        # Enable incremental authorization. Recommended as a best practice.
        include_granted_scopes='true',
        # state='' << this is an optional, artbitrary pass through parameter that would get sent to /auth-callback if provided. See https://developers.google.com/identity/protocols/oauth2/web-server#python
    )
    return(flask.redirect(authorization_url))
    

@bp.route("/auth-callback")
def google_oauth2_callback():
    """ This is the callback url for Google OAuth2 """
    
    secrets = get_oauth_details()
    #state = flask.session['state']
    scopes = ' '.join(get_scopes('import'))

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        'conf/google_client_secret.json',
        scopes=scopes,
        #state=state,
    )
    flow.redirect_uri = secrets['url']
    authorization_response = flask.request.url
    try:
        flow.fetch_token(authorization_response=authorization_response)
    except oauthlib.oauth2.rfc6749.errors.AccessDeniedError as ae:
        return(flask.current_app.send_static_file('auth/error-access-denied.html'))
    except Warning as warn:
        return(flask.current_app.send_static_file('auth/error-incomplete-access.html'))

    # Store the credentials in the session.
    credentials = flow.credentials
    flask.session['google_token'] = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'scopes': credentials.scopes,
    }

    return(flask.current_app.send_static_file('auth/googleauth-callback.html'))

def api(service_path, method_list, params=None):
    if 'google_token' not in flask.session or not flask.session['google_token']:
        return({'error': "Not logged into Google.", 'status_code': 401})
    
    if not params:
        params = {}

    # Load credentials from the session.
    secrets = get_oauth_details()
    creds = {'client_id': secrets['client'], 'client_secret': secrets['secret']}
    creds.update(flask.session['google_token'])
    creds['scopes'] = creds['scopes'].split(' ')
    credentials = google.oauth2.credentials.Credentials(**creds)
        
    service = googleapiclient.discovery.build(
        *service_path, credentials=credentials
    )
    method = service
    last_method = method_list.pop()
    for next_method in method_list:
        method = getattr(method, next_method)()

    result = getattr(method, last_method)(**params).execute()
    return(result)

@bp.route("/getme", methods=('GET', 'POST'))
def google_get_authenticated_user():
    try:
        authuser = api(
            service_path=['oauth2','v2'],
            method_list=['userinfo','get'] 
        )
    except google.auth.exceptions.RefreshError as referr:
        # - this means the token is out and needs to be 
        flask.session['google_token'] = None
        return({'error': "Not logged into Google.", 'status_code': 401})
    return(authuser)

    if 'google_token' not in flask.session or not flask.session['google_token']:
        return({'error': "Not logged into Google.", 'status_code': 401})
    
    # Load credentials from the session.
    secrets = get_oauth_details()
    creds = {'client_id': secrets['client'], 'client_secret': secrets['secret']}
    creds.update(flask.session['google_token'])
    creds['scopes'] = creds['scopes'].split(' ')
    print(json.dumps(creds))
    credentials = google.oauth2.credentials.Credentials(**creds)
        
    user_info_service = googleapiclient.discovery.build(
        'oauth2','v2', credentials=credentials
    )
    user_info = user_info_service.userinfo().get().execute()

    print(f"User info:  {user_info}", file=sys.stderr)
    
    return(user_info)

@bp.route("/getfiles", methods=('GET', 'POST'))
def get_files():


    if 'google_token' not in flask.session or not flask.session['google_token']:
        return({'error': "Not logged into Google.", 'status_code': 401})

    # Load credentials from the session.
    credentials = google.oauth2.credentials.Credentials(
        **flask.session['google_token']
    )

    search_value = 'mimeType="application/vnd.google-apps.document" and trashed=false'
    
    name = flask.request.values.get('name_contains')
    search_value += f' and name contains "{name}"'

    all_drives = flask.request.values.get('all_drives')
    print(f"ALL DRIVES = {all_drives}")
    #drive = googleapiclient.discovery.build(
    #    'drive', 'v3', credentials=credentials, 
    #)

    filedata = api(
        service_path=['drive','v3'],
        method_list=['files','list'],
        params={
            'includeItemsFromAllDrives': all_drives,
            'supportsAllDrives': all_drives,
            'pageSize': 50,
            'q':search_value,
        } 
    )

    #filedata = drive.files().list(
    #    includeItemsFromAllDrives=all_drives,
    #    supportsAllDrives=all_drives,
    #    pageSize=50,
    #    q=search_value
    #).execute()

    if 'nextPageToken' in filedata and filedata['nextPageToken']:
        return({'success':False, 'result_count_exceeded':True})
    return (flask.jsonify(filedata['files']))
    

@bp.route('/logout', methods=('GET', 'POST'))
def googlelogout():

    if 'google_token' not in flask.session or not flask.session['google_token']:
        raise Exception("You are not presently logged into Google, so you cannot log out.")

    creds = flask.session['google_token']
    resp = requests.post('https://oauth2.googleapis.com/revoke',
        params={'token': creds['token']},
        headers = {'content-type': 'application/x-www-form-urlencoded'}
    )
    flask.session['google_token'] = None
    if resp.ok:
        return({'logout': 'successful'})
    else:
        return({
            'error': ['Failed to log out'],
            'status_code': resp.status_code,
            'json': resp.json()
        })

@bp.route('/refresh', methods=('GET', 'POST'))
def googlerefresh():


    authorization_url, state = flow.authorization_url(
        # Enable offline access so that you can refresh an access token without
        # re-prompting the user for permission. Recommended for web server apps.
        access_type='offline',
        # Enable incremental authorization. Recommended as a best practice.
        include_granted_scopes='true',
    )

