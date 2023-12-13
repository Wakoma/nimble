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
