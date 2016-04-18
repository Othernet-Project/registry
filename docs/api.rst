************
Registry API
************


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
