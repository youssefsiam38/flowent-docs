# Flowent API Gateway Documentation

Documentation for the Flowent API Gateway - a system for registering and managing custom actions in Flowent conversational flows.

## About

The Flowent API Gateway enables external developers to extend Flowent with custom webhook-based actions. This documentation provides:

- **Getting Started**: Quick start guide for registering your first action
- **API Concepts**: Detailed explanation of authentication, webhooks, and security
- **Integration Guide**: Information on migrating and integrating with existing systems
- **Code Examples**: Complete implementation examples in Python
- **API Reference**: Full API specification and endpoints

## Development

To preview documentation changes locally, install the [Mintlify CLI](https://www.npmjs.com/package/mint):

```bash
npm i -g mint
```

Then run the following command at the root of the documentation:

```bash
mint dev
```

View your local preview at `http://localhost:3000`. The preview updates automatically as you edit files.

## Project Structure

```
flowent-docs/
├── index.mdx                    # Home page
├── quickstart.mdx              # Getting started guide
├── development.mdx             # Development setup
├── api_gateway/                # API Gateway documentation
│   ├── README.md              # Detailed API concepts
│   ├── MIGRATION.md           # Integration guide
│   ├── openapi.yaml           # OpenAPI specification
│   └── examples/              # Code examples
│       └── python/
├── api-reference/             # Auto-generated API reference
└── docs.json                  # Mintlify configuration

```

## Documentation Pages

- **Getting Started**: Introduction to Flowent API Gateway
- **Quickstart**: Register your first action in 3 steps
- **Development Setup**: Set up your local development environment
- **API Concepts**: Learn about authentication, webhooks, and security considerations
- **Integration Guide**: Migrate and integrate with existing systems
- **Code Examples**: Complete working examples in Python
- **API Reference**: Full endpoint documentation

## Publishing

Changes to the `main` branch are automatically deployed to production.

## Support

For issues, questions, or contributions, please visit the [Flowent GitHub repository](https://github.com/janan-tech/flowent).
