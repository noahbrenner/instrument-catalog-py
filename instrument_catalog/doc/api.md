General Usage
-------------

All API requests must:

* Include your API key as a Bearer token in your HTTP header.
* Send content in JSON format if the call has a request body.

**HTTP Example:**

```
POST <your_endpoint_of_choice>
Authorization: Bearer <your_API_key>
Content-Type: application/json
...

{"your":"request body"}
```

**`curl` Examples:**

```bash
# Simple GET request
curl -H "Authorization: Bearer $API_KEY" "$API_BASE/categories/"

# PUT request
curl -H "Authorization: Bearer $API_KEY" \
     -H "Content-Type: application/json" \
     -X PUT \
     -d '{"category_id": 2}' \
     "$API_BASE/instruments/1/"
```

Please note that there is a rate limit enforced which is currently 50 requests per minute or 2 requests per second, whichever is reached first. This limit applies to all endpoints collectively. If you go over the rate limit, you will receive a status code of `429 Too Many Requests`.

Responses
---------

All responses are JSON objects with the following content:

* `successful` (boolean): Whether or not the request succeeded.
* `errors` (array[string]): Descriptions of each request error that was detected.
* `data` (object or list[object]): The data you requested, if successful, otherwise an empty object. Every object returned, whether alone or in an array, is either a Category Object or an Instrument Object with the exception of `DELETE` requests (see below for details).

The documentation for each endpoint will only describe the contents of `data` upon a successful request, as the other keys are identical for every endpoint.

**Example:**

```json
{
    "successful": false,
    "errors": [
        "Unknown API Endpoint"
    ],
    "data": {}
}
```

### Category Object

A `Category Object` describes a category of instruments. It has the following content:

* `id` (integer): The category's unique ID.
* `name` (string): The category's name.
* `description` (string): The category's description in markdown format.

**Example:**

```json
{
    "id": 1,
    "name": "Strings",
    "description": "# A heading\n\nSome *emphasized* text."
}
```

### Instrument Object

An `Instrument Object` describes a single instrument. It has the following content:

* `id` (integer): The instrument's unique ID.
* `name` (string): The instrument's name.
* `description` (string): The instrument's description in markdown format.
    * It should be written purely in markdown; literal HTML will be escaped.
* `image` (string or null): If not `null`, a URL pointing to an image of the instrument.
    * It must use `https` or `http` (`https` is preferred).
    * It must point to a JPEG, PNG, or GIF image.
    * The image must be under 300 KB (smaller is preferred)
    * Images that are close to square are preferred.
* `category_id` (integer): The ID for the category to which this instrument belongs.
* `alternate_names` (array[string]): An ordered list of alternate names for the instrument. The array may be empty.
    * There must be no duplicates in the list.
    * No alternate name may duplicate the primary name.

**Example:**

```json
{
    "id": 1,
    "name": "Pedal Harp",
    "description": "# A heading\n\nSome *emphasized* text.",
    "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/94/Harp.svg/220px-Harp.svg.png",
    "category_id": 1,
    "alternate_names": [
        "Concert Harp",
        "Orchestral Harp"
    ]
}
```

Endpoints
---------

### `GET /myinstruments/`

Get the full list of instruments that you have created.

#### Response `data`

An array of Instrument Objects.


### `GET /categories/`

Get the full list of instrument categories.

#### Response `data`

An array of Category Objects.


### `GET /categories/<category_id>/`

Get data on a single instrument category.

#### URL Parameter

`category_id` (integer): The ID of the category for which you are requesting data.

#### Response `data`

A single Category Object.


### `GET /categories/<category_id>/instruments/`

Get the list of instruments belonging to a single category.

#### URL Parameter

`category_id` (integer): The ID of the category for which you are requesting data.

#### Response `data`

An array of Instrument Objects.


### `GET /instruments/`

Get the full list of instruments in the Instrument Catalog.

#### Response `data`

An array of Instrument Objects.


### `POST /instruments/`

Create a new instrument.

#### JSON Request Parameters

An instrument object, but with the following options and restrictions:

* Required parameters
    * `name` (string)
    * `description` (string)
    * `category_id` (integer)
* Optional parameters
    * `image` (string or null)
    * `alternate_names` (array[string])
* Forbidden parameters
    * `id` (integer)
    * Any other key not named here

#### Response `data`

A single Instrument Object. Some transformations may be performed on your submitted data, such as removing excess whitespace.


### `GET /instruments/<instrument_id>/`

Get data on a single instrument.

#### URL Parameter

`instrument_id` (integer): The ID of the category for which you are requesting data.

#### Response `data`

A single Instrument Object.


### `PUT /instruments/<instrument_id>/`

Update an instrument's data. For the request to succeed, you must be authenticated using the API key for the account that created this instrument.

#### URL Parameter

`instrument_id` (integer): The ID of the instrument that you are attempting to modify.

#### JSON Request Parameters

An instrument object, but with the following options and restrictions:

* Required parameters
    * None
* Optional parameters
    * `name` (string)
    * `description` (string)
    * `category_id` (integer)
    * `image` (string or null)
    * `alternate_names` (array[string])
* Forbidden parameters
    * `id` (integer)
    * Any other key not named here

Only the specified Instrument Object attributes are updated, others are left unchanged. If there are any errors in the request, no changes are made.

#### Response `data`

A single Instrument Object. Some transformations may be performed on your submitted data, such as removing excess whitespace.


### `DELETE /instruments/<instrument_id>/`

Delete an instrument from the Instrument Catalog. For the request to succeed, you must be authenticated using the API key for the account that created this instrument.

#### URL Parameter

`instrument_id` (integer): The ID of the instrument that you are attempting to delete.

#### Response `data`

An object with a key of `"deleted_instrument_id"` and a value of the ID that the deleted instrument had before it was deleted.

**Example:**

```json
{
    "deleted_instrument_id": 1
}
```

This request is idempotent; multiple requests will all return a status of `200 OK`.
