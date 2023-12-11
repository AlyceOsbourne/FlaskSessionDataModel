# Flask Session Data Module

Welcome to the Flask Session Data module, a robust tool designed for efficient session data management in your Flask
applications. The `sessiondata.py` file provided in this repository contains classes, functions, and utilities that
streamline the handling of session data within Flask.

### SessionData Class

The `SessionData` class, an extension of `types.SimpleNamespace` and `typing.MutableMapping`, serves as the foundational
representation of session data. It simplifies attribute setting and deletion, encodes and decodes session data, and
seamlessly integrates with Flask sessions.

### EncryptedSessionData Class

Extending the capabilities of `SessionData`, the `EncryptedSessionData` subclass overrides the encode and decode methods
to encrypt and decrypt session data. The secret key is used as the encryption key, and as such, the secret key should be 
32 base64-encodable bytes.
If you are unsure, you can pad the bytes with `=` until the length is 32.

### init_app Function

Utilize the `init_app` function to initialize your Flask application with the designated session data classes. This
function also configures endpoints for retrieving session data and injects the data into the Flask context.

## Usage

To effectively leverage this module, define your own session data classes that inherit from either `SessionData`
or `EncryptedSessionData`. Then, initialize your Flask application by passing these classes to the `init_app` function.

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
SessionData object, and upon exiting the context, the data is stored to the user's client.

Accessing data in templates is straightforward. For instance:

```html
{% if user.theme == "light" %}
<link rel="stylesheet" href="{{ url_for('static', filename='css/light.css') }}">
{% else %}
<link rel="stylesheet" href="{{ url_for('static', filename='css/dark.css') }}">
{% endif %}
```

Additionally, a developer API endpoint is available to view session data. Following the example, the endpoint would
be `/api/user`, returning a JSON object with the session data. This also supports querying individual and multiple
attributes, e.g., `/api/user?theme` and `/api/user?theme&name`.

## Requirements

This module is compatible with Python 3.8 or later and relies on the following Python packages:

- Flask
- cryptography

## License

This project is licensed under the MIT license for your convenience. Feel free to explore and adapt it to suit your
needs.