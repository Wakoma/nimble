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

The server can then be tested with curl, and an example is given below.

```
curl -X GET \
  -H "Content-type: application/json" \
  -H "Accept: application/json" \
  -d '{"config":{"rack_position_1": "X Router"}}' \
  "http://127.0.0.1:8000/wakoma/nimble"
```
