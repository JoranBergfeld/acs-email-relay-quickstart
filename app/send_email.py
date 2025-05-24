#!/usr/bin/env python3
"""
Azure Communication Services Email Sample - Multiple Recipients
This script demonstrates how to send emails to multiple recipients 
using Azure Communication Services Email SDK.
"""

import os
import time
from azure.communication.email import EmailClient
from azure.identity import DefaultAzureCredential, ManagedIdentityCredential
from dotenv import load_dotenv

# Configuration Constants
POLLER_WAIT_TIME = 10
MAX_TIMEOUT_SECONDS = 180

# Load environment variables from .env file if it exists
load_dotenv()

def create_email_client():
    """Create an email client using managed identity or environment variables"""
    # Get ACS resource name from environment variables
    acs_name = os.environ.get("ACS_NAME")
    if not acs_name:
        raise ValueError("Missing required environment variable: ACS_NAME")
        
    endpoint = f"https://{acs_name}.communication.azure.com"
    
    # Authentication priority:
    # 1. Managed identity if running in Azure with user-assigned identity
    # 2. Connection string if provided
    # 3. DefaultAzureCredential for local development with az login
    
    # Check for managed identity client ID 
    managed_identity_client_id = os.environ.get("MANAGED_IDENTITY_CLIENT_ID")
    
    try:
        # First try with user-assigned managed identity if client ID is provided
        if managed_identity_client_id:
            credential = ManagedIdentityCredential(client_id=managed_identity_client_id)
            return EmailClient(endpoint=endpoint, credential=credential)
            
        # Fall back to connection string if provided
        connection_string = os.environ.get("ACS_CONNECTION_STRING")
        if connection_string:
            return EmailClient.from_connection_string(connection_string)
            
        # Try with DefaultAzureCredential for local development
        credential = DefaultAzureCredential()
        return EmailClient(endpoint=endpoint, credential=credential)
        
    except Exception as e:
        print(f"Error creating email client with managed identity: {e}")
        
        # Final fallback to access key if available
        access_key = os.environ.get("ACS_ACCESS_KEY") or os.environ.get("AZURE_APP_REGISTRATION_CLIENT_SECRET")
        if access_key:
            connection_string = f"endpoint={endpoint};accesskey={access_key}"
            return EmailClient.from_connection_string(connection_string)
            
        # Re-raise the original exception if no fallback works
        raise

def send_email_to_multiple_recipients(sender_address, to_recipients, cc_recipients=None, bcc_recipients=None):
    """Send an email to multiple recipients"""
    
    # Create email client
    try:
        client = create_email_client()
        
        # Format recipients
        to_list = [{"address": recipient} for recipient in to_recipients]
        cc_list = [{"address": recipient} for recipient in cc_recipients] if cc_recipients else []
        bcc_list = [{"address": recipient} for recipient in bcc_recipients] if bcc_recipients else []
        
        # Create email message
        message = {
            "senderAddress": sender_address,
            "recipients": {
                "to": to_list,
                "cc": cc_list,
                "bcc": bcc_list
            },
            "content": {
                "subject": "Test email from Azure Communication Services Python Sample",
                "plainText": "This is the plain text content of the test email.",
                "html": "<html><h1>Hello from ACS Email!</h1><p>This is an <strong>HTML</strong> email sent using the <em>Azure Communication Services</em> Email SDK.</p></html>"
            }
        }
        
        print(f"Sending email from {sender_address} to {', '.join(to_recipients)}")
        
        # Send the email
        poller = client.begin_send(message)
        
        # Wait for the operation to complete
        time_elapsed = 0
        while not poller.done():
            print(f"Email send poller status: {poller.status()}")
            poller.wait(POLLER_WAIT_TIME)
            time_elapsed += POLLER_WAIT_TIME
            
            if time_elapsed > MAX_TIMEOUT_SECONDS:
                raise RuntimeError("Polling timed out.")
        
        # Check the result
        result = poller.result()
        if result["status"] == "Succeeded":
            print(f"Successfully sent the email (operation id: {result['id']})")
        else:
            print(f"Failed to send email: {result}")
            
    except Exception as ex:
        print(f"Error sending email: {ex}")

def main():
    """Main function"""
    # Get sender address from environment variables
    sender_address = os.environ.get("FROM_EMAIL_ADDRESS")
    if not sender_address:
        # Try to construct it from sender domain
        sender_domain = os.environ.get("FROM_SENDER_DOMAIN")
        if sender_domain:
            sender_address = f"DoNotReply@{sender_domain}"
        else:
            print("Sender information not found in environment variables. Please set FROM_EMAIL_ADDRESS or FROM_SENDER_DOMAIN.")
            return

    # Get recipients from environment variables (comma-separated)
    to_recipients = os.environ.get("TO_RECIPIENTS")
    cc_recipients = os.environ.get("CC_RECIPIENTS")
    bcc_recipients = os.environ.get("BCC_RECIPIENTS")

    # Parse recipients into lists, fallback to sample if not set
    to_recipients = [email.strip() for email in to_recipients.split(",") if email.strip()] if to_recipients else ["recipient1@example.com", "recipient2@example.com"]
    cc_recipients = [email.strip() for email in cc_recipients.split(",") if email.strip()] if cc_recipients else ["cc_recipient@example.com"]
    bcc_recipients = [email.strip() for email in bcc_recipients.split(",") if email.strip()] if bcc_recipients else ["bcc_recipient@example.com"]

    # Send email to multiple recipients
    send_email_to_multiple_recipients(
        sender_address=sender_address,
        to_recipients=to_recipients,
        cc_recipients=cc_recipients,
        bcc_recipients=bcc_recipients
    )

if __name__ == "__main__":
    main()
