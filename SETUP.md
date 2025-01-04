# Configuring the OSF-URE Tools

This document describes the procedures to set up and configure the OSF/URE Tools
for individual running. This is intended to be the initial configuration and setup
document and you likely do not need to reference it after initial setup.

In constrast, the [RUNTIME.md](RUNTIME.md) document provides details about the 
tools, features, and existing codebase. It provides more guidance for active development.

The [README.md](README.md) provides an overview of the project.

# OSF API and Developer Setup

You need the API Key to connect to the [OSF API](https://developer.osf.io/).

## Setup on the OSF Platform

Go to [OSF Setting](https://osf.io/settings/).

In [Personal Access Tokens (PAT)](https://osf.io/settings/tokens), create a
token with `osf.full_write` scopes, which is necessary for the Importer.
Obviously you can also create a token with just `full_read` if you will be
segmenting the Importer from other tools. This will give you a new PAT - you can
not retrieve it anytime after it is created, so copy it down.

In [Developer Apps](https://osf.io/settings/applications), Create an app and 
set the **Authorization Callback URL** to
`http://localhost:3000/auth/osfauth-callback.html`
for local development, or whatever it would be for deployment. This will give
you the **OSF Client ID** and **Client Secret**.

**NOTE:** It seems that OSF may now require the Callback URL to have the 
`https` protocol, which would require your test server to have an SSL 
certificate for your local dev server instance. I'm not sure of this, as our 
DEV app does not but I was recently unable to create a new app. If this is the
case, it's annoying and you will need to generate a self-signed certificate.

## Configure Secrets for OSF

In `conf/osf.pat`, put the PAT secret value in plain text with no whitespace.

In `conf/auth.yml`, add the **Client ID**, **Client Secret**, and **Callback URL**  
with the  appropriate context. Currently, the repo supports the following contexts:

- `production` is obviously the public facing system.
- `staging` is the for a "real" webserver for final integration testing.
- `development` is for local development and testing.

```sh
development:
  client: <idididididid>
  secret: <secretsecretsecret>
  url: http://localhost:3000/auth/osfauth-callback.html
```

# Google Developer Setup

## Project Registration

Connecting to Google Docs / Drive requires configuring a Google developer account
and using Google's OAuth Authentication platform.  

Go to [Google Cloud](https://console.cloud.google.com/) and create new project.

## Enable APIs

Go to the [APIs & Services](https://console.cloud.google.com/apis/dashboard)
and enable:

- Google Drive
- Google Docs

## Set Up OAuth Credentials

Create an OAuth 2.0 credential. Go to the 
[Google Auth Page](https://console.cloud.google.com/auth)

This will require:

- Configuring the consent screen.
- In **Audience**, add email addresses (that must have Google accounts attached to them) of test users who are allowed to access the development app.
- In **Clients**, create an OAuth Client for a **Web Application**:
    - Ensure that the URIs for both real and test servers are added as JavaScript origins
    - Ensure the URIs fo both real and test cleints are added as redirect URIs
    - Include both `http://localhost` and `http://localhost:3000` for local development. 
    - The current codebase expects redirect URIs to `/google/auth-callback`, so set the Auth Redirect accordingly (e.g., `http://localhost:3000/google/auth-callback` for local development)
- Download the **OAuth Client JSON** and place at `conf/google_client_secret.json`

## Configure Secrets for Google

As noted above, the **OAuth Client** JSON file should be downloaded and placed
at `conf/google_client_secret.json`

In `conf/googleauth.yml`, add the **Client ID**, **Client Secret**, 
and **Authorized redirect URI** with the  appropriate context. 

For example:

```sh
development:
    client: <somethingsomethingsomething>.apps.googleusercontent.com
    secret: <secretsecretsecret-moresecretmoresecret>
    url: http://localhost:3000/google/auth-callback
```

# Runtime Environment Setup

This code has been built on Ubuntu linux systems and deployed in various linux 
environments. 

It has not been run or tested on Windows or MacOS. Good luck.

## External Program Requirements

`pandoc` version 3 is required on the server for the importer and 
must be installed. 

On Ubuntu, this can be done with:

```sh
apt install pandoc
```

# Python Setup

This repo is built on vanilla Python 3.10 and it is highly recommended to use 
a virtual environment. 

It has not been tested with Conda or similar platforms. 

## Install Python Requirements

The `requirements.txt` file includes both required packages and the "in-house"
packages in `pkg` and should be all you need.

```sh
pip install -r requirements.txt
```

