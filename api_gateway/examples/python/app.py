"""
Flowent API Gateway Python Example
==================================

This example shows how to implement a Flowent action server using Python Flask.
It includes proper HMAC validation, error handling, and logging.

IMPORTANT: This example correctly implements HMAC signature validation by calculating
the signature on the payload WITHOUT the signature field, which matches how Flowent
generates the signatures on the server side.
"""

import hmac
import hashlib
import json
import logging
import time
from typing import Dict, Any, Tuple
from flask import Flask, request, jsonify
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuration - these should be environment variables in production
FLOWENT_API_URL = "https://your-flowent-instance.com/api/v1/gateway"
API_TOKEN = "your-api-token-here"
HMAC_KEY = "your-hmac-key-here"

class FlowentActionServer:
    def __init__(self, hmac_key: str):
        self.hmac_key = hmac_key.encode('utf-8')
    
    def validate_signature(self, request_data: Dict[str, Any], received_signature: str) -> bool:
        """
        Validate HMAC signature for incoming requests.
        
        CRITICAL: The signature is calculated on the payload WITHOUT the signature field.
        """
        # Create payload without signature field (as Flowent does)
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
            self.hmac_key,
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        logger.debug(f"Payload without signature: {payload}")
        logger.debug(f"Expected signature: {expected_signature}")
        logger.debug(f"Received signature: {received_signature}")
        
        return hmac.compare_digest(received_signature, expected_signature)
    
    def debug_signature_validation(self, request_data: Dict[str, Any], received_signature: str) -> bool:
        """
        Debug version of signature validation with detailed logging.
        Use this function when troubleshooting signature validation issues.
        """
        logger.info("=== SIGNATURE VALIDATION DEBUG ===")
        logger.info(f"Full request data: {json.dumps(request_data, indent=2)}")
        
        # Create payload without signature field
        payload_without_signature = {
            "action_name": request_data["action_name"],
            "parameters": request_data["parameters"],
            "timestamp": request_data["timestamp"]
        }
        
        if "test" in request_data:
            payload_without_signature["test"] = request_data["test"]
        
        payload = json.dumps(payload_without_signature, separators=(',', ':'))
        expected_signature = hmac.new(
            self.hmac_key,
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        logger.info(f"Payload without signature: {payload}")
        logger.info(f"HMAC key length: {len(self.hmac_key)} bytes")
        logger.info(f"Expected signature: {expected_signature}")
        logger.info(f"Received signature: {received_signature}")
        logger.info(f"Signatures match: {hmac.compare_digest(received_signature, expected_signature)}")
        logger.info("================================")
        
        return hmac.compare_digest(received_signature, expected_signature)
    
    def execute_action(self, action_name: str, parameters: Dict[str, Any]) -> Tuple[str, int, str]:
        """
        Execute the requested action.
        
        Returns:
            tuple: (result, error)
        """
        try:
            if action_name == "send_email":
                return self.send_email(parameters)
            elif action_name == "create_user":
                return self.create_user(parameters)
            elif action_name == "get_weather":
                return self.get_weather(parameters)
            else:
                return "", 0, f"Unknown action: {action_name}"
        except Exception as e:
            logger.error(f"Action execution failed: {e}")
            return "", 0, f"Action execution failed: {str(e)}"
    
    def send_email(self, params: Dict[str, Any]) -> Tuple[str, int, str]:
        """Send an email action."""
        recipient = params.get("recipient")
        subject = params.get("subject")
        body = params.get("body")
        
        if not all([recipient, subject, body]):
            return "", 0, "Missing required parameters: recipient, subject, body"
        
        # Simulate email sending
        logger.info(f"Sending email to {recipient} with subject: {subject}")
        
        # In a real implementation, you would integrate with an email service
        # like SendGrid, Amazon SES, etc.
        time.sleep(0.1)  # Simulate API call delay
        
        return f"Email sent successfully to {recipient}", 1, ""
    
    def create_user(self, params: Dict[str, Any]) -> Tuple[str, int, str]:
        """Create a user action."""
        username = params.get("username")
        email = params.get("email")
        full_name = params.get("full_name")
        
        if not all([username, email]):
            return "", 0, "Missing required parameters: username, email"
        
        # Simulate user creation
        logger.info(f"Creating user: {username} ({email})")
        
        # In a real implementation, you would create the user in your database
        user_id = f"user_{int(time.time())}"
        
        return f"User created successfully with ID: {user_id}", 1, ""
    
    def get_weather(self, params: Dict[str, Any]) -> Tuple[str, int, str]:
        """Get weather information action."""
        location = params.get("location")
        
        if not location:
            return "", 0, "Missing required parameter: location"
        
        try:
            # Simulate weather API call
            logger.info(f"Getting weather for: {location}")
            
            # In a real implementation, you would call a weather API
            weather_data = {
                "location": location,
                "temperature": "22°C",
                "condition": "Sunny",
                "humidity": "65%"
            }
            
            result = f"Weather in {location}: {weather_data['temperature']}, {weather_data['condition']}"
            return result, 1, ""
            
        except Exception as e:
            return "", 1, f"Failed to get weather data: {str(e)}"

# Initialize the action server
action_server = FlowentActionServer(HMAC_KEY)

@app.route('/actions/<action_name>', methods=['POST'])
def handle_action(action_name: str):
    """Handle incoming action requests from Flowent."""
    try:
        # Get request data
        payload = request.get_data(as_text=True)
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "Invalid JSON payload"}), 400
        
        # Handle test requests during action registration
        if data.get("test", False):
            logger.info(f"Received test request for action: {action_name}")
            return jsonify({
                "result": f"Test successful for action: {action_name}",
                "error": ""
            }), 200
        
        # Validate HMAC signature for non-test requests
        # NOTE: Signature is calculated on payload WITHOUT the signature field
        signature = data.get("signature", "")
        if not signature:
            return jsonify({"error": "Missing signature"}), 401
        
        if not action_server.validate_signature(data, signature):
            logger.warning("Invalid signature received")
            return jsonify({"error": "Invalid signature"}), 401
        
        # Validate timestamp (optional, prevents replay attacks)
        timestamp = data.get("timestamp", 0)
        current_time = int(time.time())
        if abs(current_time - timestamp) > 300:  # 5 minute window
            return jsonify({"error": "Request timestamp too old"}), 401
        
        # Execute the action
        parameters = data.get("parameters", {})
        result, error = action_server.execute_action(action_name, parameters)
        
        response = {
            "result": result,
            "error": error
        }
        
        if error:
            logger.error(f"Action {action_name} failed: {error}")
            return jsonify(response), 500
        else:
            logger.info(f"Action {action_name} completed successfully")
            return jsonify(response), 200
            
    except Exception as e:
        logger.error(f"Unexpected error handling action {action_name}: {e}")
        return jsonify({
            "result": "",
            "error": f"Internal server error: {str(e)}"
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "timestamp": int(time.time())}), 200

@app.route('/actions', methods=['GET'])
def list_available_actions():
    """List available actions (for documentation purposes)."""
    actions = [
        {
            "name": "send_email",
            "description": "Send an email to a specified recipient",
            "parameters": ["recipient", "subject", "body"]
        },
        {
            "name": "create_user", 
            "description": "Create a new user account",
            "parameters": ["username", "email", "full_name"]
        },
        {
            "name": "get_weather",
            "description": "Get weather information for a location",
            "parameters": ["location"]
        }
    ]
    return jsonify({"actions": actions}), 200

def register_actions_with_flowent():
    """Register actions with Flowent API Gateway."""
    # First, exchange API token for JWT
    response = requests.post(f"{FLOWENT_API_URL}/token/exchange", json={
        "api_token": API_TOKEN
    })
    
    if response.status_code != 200:
        logger.error(f"Token exchange failed: {response.text}")
        return
    
    jwt_token = response.json()["jwt_token"]
    headers = {"Authorization": f"Bearer {jwt_token}"}
    
    # Define actions to register
    actions_to_register = [
        {
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
        },
        {
            "name": "create_user",
            "description": "Create a new user account",
            "webhook_url": "https://your-server.com/actions/create_user",
            "json_schema": {
                "type": "object",
                "properties": {
                    "username": {
                        "type": "string",
                        "description": "Unique username for the account"
                    },
                    "email": {
                        "type": "string",
                        "description": "User's email address"
                    },
                    "full_name": {
                        "type": "string",
                        "description": "User's full name"
                    }
                },
                "required": ["username", "email"]
            }
        },
        {
            "name": "get_weather",
            "description": "Get weather information for a location",
            "webhook_url": "https://your-server.com/actions/get_weather",
            "json_schema": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "Location to get weather for"
                    }
                },
                "required": ["location"]
            }
        }
    ]
    
    # Register each action
    for action_data in actions_to_register:
        response = requests.post(
            f"{FLOWENT_API_URL}/actions",
            headers=headers,
            json=action_data
        )
        
        if response.status_code == 201:
            logger.info(f"Action '{action_data['name']}' registered successfully")
        elif response.status_code == 409:
            logger.info(f"Action '{action_data['name']}' already exists")
        else:
            logger.error(f"Failed to register action '{action_data['name']}': {response.text}")

if __name__ == '__main__':
    # Register actions on startup (comment out in production)
    # register_actions_with_flowent()
    
    # Start the server
    app.run(host='0.0.0.0', port=5000, debug=False)