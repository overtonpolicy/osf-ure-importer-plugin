"""
Copyright (c) 2024, Kevin Crouse. 

This file is part of the *URE Methods Plugin Repository*, located at 
https://github.com/kcphila/osf-ure-plugins

This file is distributed under the terms of the GNU General Public License 3.0
and can be used, shared, or modified provided you attribute the original work 
to the original author, Kevin Crouse.

See the README.md in the root of the project directory, or go to 
http://www.gnu.org/licenses/gpl-3.0.html for license details.
"""

import flask
import requests
import yaml
import urllib
import sys

from . import osf

bp = flask.Blueprint('auth', __name__, url_prefix='/auth')

def app_hostname():
    """ Returns a formatted hostname for the server - this is important because OSF only recognizes very specific hostnames, even when multiple strings are equivalent."""
    hostname = flask.request.url_root

    if hostname == 'http://127.0.0.1:3000/' or hostname == 'http://localhost:3000/':
        return("http://localhost:3000/") # make sure it's the exact text we registered with OSF
    return(hostname)

def development_level():
    hostname = app_hostname()

    if hostname == 'http://localhost:3000/':
        dev_mode = 'development'
    elif hostname == 'https://importer.ure-test.overton.io/':
        dev_mode = 'staging'
    elif hostname == 'https://plugins.uremethods.org/':
        dev_mode = 'production'
    else:
        raise Exception(f"We do not recognize calls from {hostname}. Connection to OSF relies on registered domain origins only. Are you perhaps using an ip address?");    
    return(dev_mode)

def osf_callback_url():
    """ This is the callback url that is registered in OSF, which is dependent on the hostname. """
    return(app_hostname() + 'auth/osfauth-callback.html')

def get_oauth_details():
    """ This is the client id that is registered in OSF and tied ot the hostname. """
    dev_mode = development_level()

    with open('conf/auth.yml') as fh:
        secrets = yaml.load(fh, Loader=yaml.CLoader)

    if dev_mode not in secrets:
        raise Exception(f"Cannot find mode '{dev_mode}' in the OSF Oauth Configuration")
    return(secrets[dev_mode])

@bp.route('/getclient', methods=['POST'])
def getclient():
    """ The sole use of this endpoint is to return the data necessary to open the oauth2 popup window. The rest of this is handled in javascript, but to keey the client id out code easily viewable in the web app, we return it here. See the OSFAuth.launchAuthWindow method in static/js/osfauth.js for where it is used  """    
    secrets = get_oauth_details()
    return({
        'oauth_client_id': secrets['client'],
        'oauth_callback_url': secrets['url'], 
    })

@bp.route('/osfauth-callback.html')
def oauth2_callback():
    """ The sole use of this endpoint is to receive the authorization code from OSF for oauth2 authentication. This is the callback_uri/redirect_uri where authorization data is sent."""
        
    return(flask.current_app.send_static_file('auth/osfauth-callback.html')) # does this need to be hard coded?


@bp.route('/debugsession', methods=['GET'])
def debugsession():
    return(f"""
    <html><body>
    <h1>Access</h1>
    {flask.session['access_token']}
    </body></html>
    """)

@bp.route('/registertoken', methods=['POST'])
def oauth2_new_token():
    """ Get the access token from an authorization code. This will automatically look up the client secret from the conf directory, which stores a mapping of client_id to client_secret in yaml format. This is called by the osf.completeAuthorization method when an access code is received back from the sign in window and is the last step for OSF authentication.
    """    
    #print("oauth2_new_token (/auth/registertoken) callback entered", file=sys.stderr)

    access_code = flask.request.values.get('access_code')
    
    if not access_code:
        raise Exception(f"Access code not provided to registertoken")
    
    url = "https://accounts.osf.io/oauth2/token"
    secrets = get_oauth_details()    

    req = requests.post(url, data={
        'client_id': secrets['client'],
        'client_secret': secrets['secret'],
        'redirect_uri': secrets['url'],
        'grant_type': 'authorization_code',
        'code': urllib.parse.unquote(access_code),
    })

    def errparams():
        return({
            'client_id': secrets['client'],
            'client_secret': '*************' + secrets['secret'][-6:],
            'redirect_uri': secrets['url'],
            'grant_type': 'authorization_code',
            'code': access_code,
        })

    if req.status_code >= 300:    
        # treat as an error
        raise Exception(f"Attempt to fetch authorization code led to status code {req.status_code}. \n\tURL: {url}\n\tReason: '{req.reason}'\n\tText: {req.text}\n\tParams: {errparams()}")

    js = req.json()
    if 'error' in js:
        js['request_params'] = errparams()
        if js['error_description'] == 'Invalid Code':
            js['error_description'] = 'Access Code is invalid or expired'
    else:
        access_token = js['access_token']        
        flask.session['access_token'] = access_token
        flask.session['token_expires'] = js['expires_in']
        #print("New access token: " + access_token, file=sys.stderr)

    return(js)


@bp.route('/login', methods=('GET', 'POST'))
def osflogin():
    if flask.request.method == 'POST':
        raise Exception('Not yet')
    return(flask.render_template('auth/login.html'))

@bp.route('/logout')
def osflogout():
    flask.session.clear()
    return(flask.redirect(flask.url_for('index')))


@bp.route('/revoketoken', methods=['GET', 'POST'])
def revoke_access_token():

    req = requests.post(
        "https://accounts.osf.io/oauth2/revoke", data={    
        'token': flask.session['access_token'],
    })

    flask.session.clear()    
    # -- the expectation here is that 
    if req.status_code == 204:
        # -- access token revoked!        
        return({'success': True})
    elif req.status_code >= 400:
        raise Exception(f"Attempted to clear the access token, but received a code {req.status_code}")
    else:
        raise Exception(f"Unknown error in attempt to revoke access. Received status code {req.status_code}, json {req.json()}")


@bp.route('/settoken', methods=['GET'])
def debug_set_token():
    """ For debugging use of authentication only: set the access token manually for the session """    
    
    access_token = flask.request.values.get('token')
    
    if not access_token:
        raise Exception(f"token url parameter required")
    
    flask.session['access_token'] = access_token
    return{'success': True}
