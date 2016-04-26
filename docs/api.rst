************
Registry API
************


Auth
====
Registry provides access to content only for authenticated clients. All 
content API calls must carry a time-limited session token, which is issued on
successful authentication.

Clients are currently registered manually and are provided with a symmetric 
encryption key. Clients should initiate authentication via ``POST /auth`` 
endpoint, specifying ``client_name``. The server uses a challenge-response 
protocol for authentication and sends a plaintext message along with cipher
details. The client should send back a encrypted version of the text, using
the registered keyi, via ``POST /auth_verify``. If the server is able to 
verify the authenticity of the encrypted text, it responds with a session 
token and a duration for which the token is valid. As long as the token is 
valid, the client has unfettered access to registry. When the token expires, 
the server will reject attempts to access the API and the client has to go 
through the cycle once again.


POST /auth
^^^^^^^^^^

This endpoint is the starting point for client authentication. The client sends
their registered ``client_name`` to begin the handshake.

Arguments
---------

+-------------+------------------------------------------------------------+----------------+
| Parameter   | Description                                                | Type           |
+=============+============================================================+================+
| client_name | Registered name of the client                              | String         |
+-------------+------------------------------------------------------------+----------------+


Response
--------
The response will be in JSON object. If the API call succeeds, the resultant
object will be of the form

.. code-block:: json

    {
        "success": true,
        "challenge": {
            "id": "...",
            "text": "...",
            "duration": ...,
            "cipher": "...",
            "cipher_iv": "...",
        }
    }

Here ``cipher`` is the cipher to be used to encrypt the plaintext ``text``. 
Currently only AES cipher in CBC mode is supported and ``cipher_iv`` must be 
used as the initialization vector. The client should send back a response 
with the matching challenge ``id`` and the encrypted text to 
``POST /auth_verify``. The client must complete the next step in ``duration``
seconds.

If the API call fails, the resultant object will be of the form 

.. code-block:: json

    {
        "success": false,
        "message": "..."
    }


POST /auth_verify
^^^^^^^^^^^^^^^^^

This endpoint is used to veify the challenge response and is the final stage 
of client authentication. The client sends their registered ``client_name`` 
along with the received challenge id and encrypted text. The client may ask 
for a session token of a specific duration, however the server makes the 
final call.

Arguments
---------

+----------------+------------------------------------------------------------+----------------+
| Parameter      | Description                                                | Type           |
+================+============================================================+================+
| client_name    | Registered name of the client                              | String         |
+----------------+------------------------------------------------------------+----------------+
| id             | Challenge id issued                                        | String         |
+----------------+------------------------------------------------------------+----------------+
| duration       | Desired session duration in seconds                        | Integer        |
+----------------+------------------------------------------------------------+----------------+
| encrypted_text | The encrypted text                                         | String         |
+----------------+------------------------------------------------------------+----------------+



Response
--------
The response will be in JSON object. If the API call succeeds, the resultant
object will be of the form

.. code-block:: json

    {
        "success": true,
        "session": {
            "token": "...",
            "duration": ...,
        }
    }

The ``token`` so received should be used to make content API calls. The token 
generated is valid for ``duration`` seconds.

If the API call fails, the resultant object will be of the form 

.. code-block:: json

    {
        "success": false,
        "message": "..."
    }


Content
=======

GET /
^^^^^

This endpoint is used to get a list of all files known to registry. It accepts
additional parameters in the query string to filter the list.

Arguments
---------

+-------------+------------------------------------------------------------+----------------+
| Parameter   | Description                                                | Type           |
+=============+============================================================+================+
| id          | Id of the file                                             | String         |
+-------------+------------------------------------------------------------+----------------+
| serve_path  | Path where a file will end up on the receiver              | Regex          |
+-------------+------------------------------------------------------------+----------------+
| path        | Absolute path of a file on local storage                   | Path           |
+-------------+------------------------------------------------------------+----------------+
| uploaded    | Unix timestamp when a file was added to registry           | Unix Timestamp |
+-------------+------------------------------------------------------------+----------------+
| since       | Unix timestamp when any file or its metadata were modified | Unix Timestamp |
+-------------+------------------------------------------------------------+----------------+
| category    | Content category                                           | String         |
+-------------+------------------------------------------------------------+----------------+
| aired       | Marked true when a file is aired                           | Boolean        |
+-------------+------------------------------------------------------------+----------------+
| alive       | Marked false if the file has been deleted                  | Boolean        |
+-------------+------------------------------------------------------------+----------------+
| count       | Maximum no of files entries to be returned                 | Integer        |
+-------------+------------------------------------------------------------+----------------+

Response
--------

The response will be in JSON object. If the API call succeeds, the resultant
object will be of the form

.. code-block:: json

    {
        "success": true,
        "results": [..],
        "count": ..
    }

With each entry in ``results`` will be of the form

.. code-block:: json

    {
        "id": 1234,
        "path": ".....",
        "size": ...,
        "uploaded": ...,
        "modified": ...,
        "category": "....",
        "expiration": ....,
        "serve_path": "....",
        "alive": ...,
        "aired": ....
    }

If the API call fails, the resultant object will be of the form

.. code-block:: json

    {
        "success": false,
        "error": "..."
    }



POST /
^^^^^^

This endpoint is used to added a new file to registry. It accepts POST 
parameters including the local path of the file

Arguments
---------

+--------------+-----------------------------------------------+---------+
| Parameter    | Description                                   | Type    |
+==============+===============================================+=========+
| serve_path * | Path where a file will end up on the receiver | String  |
+--------------+-----------------------------------------------+---------+
| path *       | Absolute path of a file on local storage      | Path    |
+--------------+-----------------------------------------------+---------+
| category     | Content category                              | String  |
+--------------+-----------------------------------------------+---------+
| aired        | Marked true when a file is aired              | Boolean |
+--------------+-----------------------------------------------+---------+

* marked fields are required

Response
--------

The response will be in JSON object. If the API call succeeds, the resultant
object will be of the form

.. code-block:: json

    {
        "success": true,
        "results": [..],
    }

with each entry in ``results`` will be of the form

.. code-block:: json

    {
        "id": 1234,
        "path": ".....",
        "size": ...,
        "uploaded": ...,
        "modified": ...,
        "category": "....",
        "expiration": ....,
        "serve_path": "....",
        "alive": ...,
        "aired": ....
    }

If the API call fails, the resultant object will be of the form

.. code-block:: json

    {
        "success": false,
        "error": "..."
    }



GET /<id>
^^^^^^^^^

This endpoint is used to download a file from the registry. The id parameter 
is the file id created when the file was added to the registry


PUT /<id>
^^^^^^^^^

This endpoint is update an existing file from the registry. The id parameter 
is the file id created when the file was added to the registry. This accepts
the same parameters as adding a new file, with a similar response


DELETE /<id>
^^^^^^^^^^^^

This endpoint *does not* delete the file from the registry, instead it marks 
the file as dead, i.e, `alive = False`. The id parameter is the file id used 
when the file was added to the registry
