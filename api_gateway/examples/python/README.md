# Flowent API Gateway Python Example

This example demonstrates how to implement a Flowent action server using Python Flask with proper HMAC signature validation.

## Key Features

- ✅ **Correct HMAC signature validation** (calculates signature on payload WITHOUT signature field)
- ✅ **Test request handling** during action registration
- ✅ **Comprehensive error handling** and logging
- ✅ **Timestamp validation** to prevent replay attacks
- ✅ **Debug utilities** for troubleshooting signature issues

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

Update the configuration variables in `app.py`:

```python
FLOWENT_API_URL = "https://your-flowent-instance.com/api/v1/gateway"
API_TOKEN = "your-api-token-here"  # From Flowent admin panel
HMAC_KEY = "your-hmac-key-here"    # From Flowent admin panel
```

## Running the Server

```bash
python app.py
```

The server will start on `http://localhost:5000`

## Available Endpoints

- `POST /actions/send_email` - Send email action
- `POST /actions/create_user` - Create user action  
- `POST /actions/get_weather` - Get weather action
- `GET /health` - Health check
- `GET /actions` - List available actions

## HMAC Signature Validation

**CRITICAL**: This example correctly implements HMAC signature validation by:

1. Receiving the full request including the signature field
2. Creating a copy of the request data WITHOUT the signature field
3. Calculating HMAC-SHA256 on the signature-free payload
4. Comparing with the received signature using constant-time comparison

This matches how Flowent generates signatures on the server side.

## Debugging Signature Issues

Use the `debug_signature_validation()` method instead of `validate_signature()` for detailed logging:

```python
# In the handler, replace:
if not action_server.validate_signature(data, signature):

# With:
if not action_server.debug_signature_validation(data, signature):
```

This will log the payload, expected signature, and received signature for comparison.

## Production Deployment

1. Use environment variables for configuration
2. Enable proper logging
3. Use a production WSGI server like Gunicorn:
   ```bash
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```
4. Implement proper error handling and monitoring
5. Use HTTPS for all webhook URLs