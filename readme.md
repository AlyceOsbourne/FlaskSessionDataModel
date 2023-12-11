# Flask Session Data Module

Welcome to the Flask Session Data module, a tool designed for efficient session data management in your Flask
applications. The `sessiondata.py` file provided in this repository contains classes, functions, and utilities that
streamline the handling of session data within Flask.

### SessionData Class

The `SessionData` class, an extension of `types.SimpleNamespace` and `typing.MutableMapping`, serves as the foundational
representation of session data. It simplifies attribute setting and deletion, encodes and decodes session data, and
seamlessly integrates with Flask sessions.

### EncryptedSessionData Class

Extending the capabilities of `SessionData`, the `EncryptedSessionData` subclass overrides the encode and decode methods
to encrypt and decrypt session data. The secret key is used as the encryption key. This is useful for when you want to
store sensitive data in the session, I do recommend in the cases where you wish to store sensitive data, make use of 
server side sessions. You only need to install the cryptography package if you wish to use this class.

### init_app Function

Utilize the `init_app` function to initialize your Flask application with the designated session data classes. This
function also configures endpoints for retrieving session data and injects the data into the Flask context.

## Usage

To effectively leverage this module, define your own session data classes that inherit from either `SessionData`
or `EncryptedSessionData`. Then, add your classes to the app configuration in a dict with the key `'SESSION_DATA_CLASSES'`.
Then call `init_app` with your Flask app.

Here's an example:

```python
class User(SessionData):
    theme: str = 'light'
    name: str = 'Unknown'


app = flask.Flask(__name__)
app.secret_key = 'secret'
app.secret_key += '=' * (32 - len(app.secret_key))
app.config['SESSION_DATA_CLASSES'] = {'user': User}

init_app(app)
```

In the provided example, a `User` session data class is defined with a `theme` attribute. The Flask application is
subsequently initialized with this session data class.

To modify session data, use the `.session` context manager of the SessionData (or subclass). This provides a modifiable
SessionData object, and upon exiting the context, the data is stored to the user's client, 
only if the data had been modified (or a new instance was created).

```python
with User.session() as user:
    user.theme = 'dark'
```

Accessing data in templates is straightforward. For instance:

```html
{% if user.theme == "light" %}
<link rel="stylesheet" href="{{ url_for('static', filename='css/light.css') }}">
{% else %}
<link rel="stylesheet" href="{{ url_for('static', filename='css/dark.css') }}">
{% endif %}
```

This feature can be disabled by setting the `INJECT_SESSION_DATA` config value to `False`.

Additionally, a developer API endpoint is available to view session data. Following the example, the endpoint would
be `/api/user`, returning a JSON object with the session data. This also supports querying individual and multiple
attributes, e.g., `/api/user?theme` and `/api/user?theme&name`.

This can be disabled by setting the `SESSION_DATA_API_ENABLED` config value to `False`.

## Requirements

This module is compatible with Python 3.8 or later and relies on the following Python packages:

- Flask
- bson
- cryptography (optional)


## Compatibility
This module is compatible with Flask-Session due to it using the same session interface,  this can further simplify
how you use server side sessions. 

GNU Lesser General Public License v3.0
PAK is licensed under the GNU General Public License v3.0. See the LICENSE file for more information.