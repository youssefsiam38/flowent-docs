# Flowent API Gateway Documentation

## Overview

The Flowent API Gateway enables external developers to register and manage custom actions that can be used within Flowent's conversational flows. This allows for extensible, tenant-specific functionality while maintaining security and reliability.

## Architecture

The API Gateway provides:

1. **Action Registration**: Register external webhook-based actions
2. **Authentication**: JWT-based authentication with API tokens
3. **Security**: HMAC signature validation for webhooks
4. **Management**: Admin panel for managing API tokens and HMAC keys

## Getting Started

### 1. Prerequisites

- Flowent instance with API Gateway enabled
- A server to host your action endpoints
- Admin access to the Flowent admin panel

### 2. Set Up Your Action Server

Your action server must:
- Accept POST requests with JSON payloads
- Validate HMAC signatures for security
- Return responses in the expected format
- Handle the test validation request during registration

### 3. Create API Credentials

1. Log into the Flowent admin panel
2. Navigate to Gateway Management
3. Create an API token for authentication
4. Create an HMAC key for webhook signature validation

### 4. Register Your Actions

Use the API Gateway endpoints to register your actions with their JSON schemas and webhook URLs.

## Authentication

### API Token Exchange

Before making any API calls, you need to exchange your API token for a JWT token:

```bash
curl -X POST https://your-flowent-instance.com/api/v1/gateway/token/exchange \
  -H "Content-Type: application/json" \
  -d '{
    "api_token": "your-api-token-here"
  }'
```

Response:
```json
{
  "jwt_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer", 
  "expires_in": 86400
}
```

### Using JWT Tokens

Include the JWT token in the Authorization header for all subsequent requests:

```bash
curl -X GET https://your-flowent-instance.com/api/v1/gateway/actions \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

## Action Management

### Register an Action

```bash
curl -X POST https://your-flowent-instance.com/api/v1/gateway/actions \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "send_email",
    "description": "Send an email to a specified recipient",
    "webhook_url": "https://your-server.com/actions/send_email",
    "json_schema": {
      "type": "object",
      "properties": {
        "recipient": {
          "type": "string",
          "description": "Email address of the recipient"
        },
        "subject": {
          "type": "string", 
          "description": "Email subject line"
        },
        "body": {
          "type": "string",
          "description": "Email body content"
        }
      },
      "required": ["recipient", "subject", "body"]
    }
  }'
```

### List Actions

```bash
curl -X GET https://your-flowent-instance.com/api/v1/gateway/actions \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Get Specific Action

```bash
curl -X GET https://your-flowent-instance.com/api/v1/gateway/actions/send_email \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Update Action

```bash
curl -X PUT https://your-flowent-instance.com/api/v1/gateway/actions/send_email \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Updated description for sending emails",
    "webhook_url": "https://your-server.com/v2/actions/send_email"
  }'
```

### Delete Action

```bash
curl -X DELETE https://your-flowent-instance.com/api/v1/gateway/actions/send_email \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Webhook Implementation

### Request Format

When Flowent executes your action, it sends a POST request to your webhook URL:

```json
{
  "action_name": "send_email",
  "parameters": {
    "recipient": "user@example.com",
    "subject": "Welcome!",
    "body": "Welcome to our service!"
  },
  "timestamp": 1645123456,
  "signature": "a8f4c2e9b1d7c3a5f2e8d6b4c1a9e7f3d5b8a2c6e4f1d9b7a3c5e8f2d6b4a1c9"
}
```

**⚠️ IMPORTANT**: The `signature` field contains the HMAC-SHA256 signature calculated on the payload WITHOUT the signature field itself. When validating, you must exclude the signature field from your HMAC calculation.

### Response Format

Your webhook must return a JSON response:

```json
{
  "result": "Email sent successfully to user@example.com",
  "error": ""
}
```

- `result`: String description of the action result
- `error`: Error message if the action failed (empty string if successful)

### Signature Validation

Validate the HMAC signature to ensure request authenticity. **CRITICAL**: The signature is calculated on the payload WITHOUT the signature field itself.

```python
import hmac
import hashlib
import json

def validate_signature(request_data, received_signature, hmac_key):
    # Create a copy of the request data WITHOUT the signature field
    payload_without_signature = {
        "action_name": request_data["action_name"],
        "parameters": request_data["parameters"], 
        "timestamp": request_data["timestamp"]
    }
    
    # Include test field if present (for validation requests)
    if "test" in request_data:
        payload_without_signature["test"] = request_data["test"]
    
    # Serialize the payload without signature (must match Flowent's serialization)
    payload = json.dumps(payload_without_signature, separators=(',', ':'))
    
    # Calculate HMAC on payload without signature
    expected_signature = hmac.new(
        hmac_key.encode('utf-8'),
        payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(received_signature, expected_signature)

# Example usage in your webhook handler
def handle_webhook(request):
    request_data = json.loads(request.body)
    received_signature = request_data.get("signature", "")
    
    if not validate_signature(request_data, received_signature, your_hmac_key):
        return {"error": "Invalid signature"}, 401
    
    # Process the valid request...
```

**Go Example:**

```go
import (
    "crypto/hmac"
    "crypto/sha256"
    "encoding/hex"
    "encoding/json"
)

func validateSignature(requestData map[string]interface{}, receivedSignature string, hmacKey []byte) bool {
    // Create payload without signature field
    payloadWithoutSig := map[string]interface{}{
        "action_name": requestData["action_name"],
        "parameters":  requestData["parameters"],
        "timestamp":   requestData["timestamp"],
    }
    
    // Include test field if present
    if test, exists := requestData["test"]; exists {
        payloadWithoutSig["test"] = test
    }
    
    // Marshal without signature field
    payload, err := json.Marshal(payloadWithoutSig)
    if err != nil {
        return false
    }
    
    // Calculate HMAC
    mac := hmac.New(sha256.New, hmacKey)
    mac.Write(payload)
    expectedSignature := hex.EncodeToString(mac.Sum(nil))
    
    return hmac.Equal([]byte(receivedSignature), []byte(expectedSignature))
}
```

**Important Notes:**
- The signature is calculated BEFORE the signature field is added to the request
- You must reconstruct the original payload by excluding the signature field
- The JSON serialization format must match exactly (use `separators=(',', ':')` in Python)
- Always use constant-time comparison (`hmac.compare_digest` or `hmac.Equal`) to prevent timing attacks

### Test Validation

During action registration, Flowent sends a test request to validate your endpoint:

```json
{
  "action_name": "your_action_name",
  "parameters": {},
  "timestamp": 1645123456,
  "test": true
}
```

Your endpoint should return a 2xx status code to pass validation.

## Security Considerations

1. **Always validate HMAC signatures** before processing requests
2. **Use HTTPS** for all webhook URLs
3. **Implement proper error handling** and logging
4. **Rate limit** your endpoints to prevent abuse
5. **Validate input parameters** against your expected schema
6. **Store HMAC keys securely** and never expose them in logs or error messages

## Error Handling

### Common Error Responses

**Invalid Token (401)**
```json
{
  "error": "Invalid token"
}
```

**Action Not Found (404)**
```json
{
  "error": "Action not found"
}
```

**Validation Failed (400)**
```json
{
  "error": "action validation failed: webhook endpoint returned status 500"
}
```

**Action Already Exists (409)**
```json
{
  "error": "action with name 'send_email' already exists"
}
```

## Best Practices

1. **Use descriptive action names** (lowercase, underscores, no spaces)
2. **Provide clear descriptions** for your actions and parameters
3. **Define comprehensive JSON schemas** with proper types and descriptions
4. **Implement proper timeout handling** (Flowent times out after 30 seconds)
5. **Log all requests and responses** for debugging
6. **Version your webhook URLs** to support updates
7. **Test your actions thoroughly** before deploying to production

## Limits and Quotas

- Maximum 100 actions per tenant
- Maximum 30-second timeout for webhook calls
- Maximum 1MB payload size
- API token valid for 24 hours
- Rate limit: 1000 requests per hour per tenant

## Troubleshooting

### Action Registration Fails

1. Verify your webhook URL is accessible
2. Check that your endpoint returns 2xx for test requests
3. Ensure your JSON schema is valid
4. Verify your JWT token is not expired

### Webhook Not Receiving Calls

1. Check action is properly registered
2. Verify webhook URL is correct and accessible
3. Ensure your server accepts POST requests
4. Check server logs for incoming requests

### Signature Validation Fails

1. **Most Common Issue**: Verify you're calculating the HMAC on the payload WITHOUT the signature field
   - The signature field should NOT be included in the HMAC calculation
   - Create a copy of the request data excluding the signature field before calculating HMAC
2. Verify you're using the correct HMAC key from the admin panel
3. Ensure your JSON serialization matches Flowent's format (`separators=(',', ':')` in Python)
4. Check for any request body modifications by middleware or reverse proxies
5. Use logging to compare your calculated signature with the received signature
6. Ensure you're using constant-time comparison functions (`hmac.compare_digest` or `hmac.Equal`)

**Debug Example:**
```python
import logging

def debug_signature_validation(request_data, received_signature, hmac_key):
    payload_without_signature = {
        "action_name": request_data["action_name"],
        "parameters": request_data["parameters"],
        "timestamp": request_data["timestamp"]
    }
    if "test" in request_data:
        payload_without_signature["test"] = request_data["test"]
    
    payload = json.dumps(payload_without_signature, separators=(',', ':'))
    expected_signature = hmac.new(hmac_key.encode(), payload.encode(), hashlib.sha256).hexdigest()
    
    logging.info(f"Payload without signature: {payload}")
    logging.info(f"Expected signature: {expected_signature}")
    logging.info(f"Received signature: {received_signature}")
    logging.info(f"Signatures match: {hmac.compare_digest(expected_signature, received_signature)}")
    
    return hmac.compare_digest(expected_signature, received_signature)
```

## Support

For additional support:
- Check the admin panel logs
- Review your webhook server logs
- Contact the Flowent team with specific error messages

## Changelog

### Version 1.0
- Initial API Gateway release
- JWT authentication
- HMAC signature validation
- Action CRUD operations
- Admin panel integration