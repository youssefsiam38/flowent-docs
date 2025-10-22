# API Gateway Examples

This directory contains example implementations for different programming languages showing how to integrate with the Flowent API Gateway.

## Examples Included

- **Python Flask**: Complete example with HMAC validation
- **Node.js Express**: TypeScript example with proper error handling
- **Go**: High-performance example with proper middleware
- **Java Spring Boot**: Enterprise-ready example

## Quick Start

Each example includes:
- Action server implementation
- HMAC signature validation
- Error handling
- Docker configuration
- Tests

Choose the example that matches your technology stack and follow the README in each directory.

## Common Patterns

### HMAC Validation

All examples show how to properly validate HMAC signatures:

1. Extract the signature from the request
2. Reconstruct the payload exactly as sent
3. Calculate the expected signature using your HMAC key
4. Compare signatures using a constant-time comparison

### Error Handling

All examples demonstrate:
- Proper HTTP status codes
- Structured error responses
- Logging for debugging
- Graceful degradation

### Testing

Each example includes:
- Unit tests for individual functions
- Integration tests with mock Flowent requests
- Load testing configurations
- Monitoring and health checks

## Security Considerations

- Never log HMAC keys or signatures
- Always use HTTPS in production
- Implement proper rate limiting
- Validate all input parameters
- Use constant-time signature comparison