# Nimble Back End Server

Back end server for Nimble documentation generation.

## Dependencies

Run the following in a Python virtual environment to install the dependencies.

```
pip install -r requirements.txt
```

## Local Usage

Run the following to run the server locally.

```
uvicorn nimble_server:app --reload
```

The server will spin up a local web page used for testing of the data flow.

`http://127.0.0.1:8000/wakoma/nimble/test_page`

The server can also be tested with curl, and an example is given below.

```
curl -X GET \
  -H "Content-type: application/json" \
  -H "Accept: application/json" \
  -d '{"config":{"server_1": "raspberry_pi_4_model_b", "router_1": "librerouter_v_1_india_version"}}' \
  "http://127.0.0.1:8000/wakoma/nimble"
```

It is also possible to request individual parts without requesting the whole assembly and its associated documents. For example, to download just the rack leg the following URL is entered into the address bar of a web browser. The parameters `length` and `model_format` can be altered in the URL as-needed.

`http://127.0.0.1:8000/wakoma/nimble/rack_leg?length=50.0&model_format=stl`

The customized rack leg should be downloaded in STL format after a short delay during generation.
