# Azure Communication Services Email - Python Samples

This directory contains Python samples for sending emails using Azure Communication Services.

## Prerequisites

- Python 3.7 or later
- Azure Communication Services Email resource (can be deployed via `azd up` from parent directory or created separately in Azure portal)

## Setup

1. Install the required Python dependencies using `uv`:

   ```bash
   uv sync
   ```

2. Configure environment variables:
   
   Copy the `.env.template` file to `.env` and update the values with your Azure Communication Services information:
   
   ```bash
   cp .env.template .env
   ```
   
   Edit the `.env` file with your values:
   ```
   # Required: ACS resource name
   ACS_NAME=your_acs_resource_name
   
   # Authentication Options (in order of preference):

   # Option 1: Managed Identity (preferred in Azure environments)
   # Client ID of the user-assigned managed identity
   # (automatically set when deployed with azd)
   MANAGED_IDENTITY_CLIENT_ID=your_managed_identity_client_id

   # Option 2: Use DefaultAzureCredential 
   # Make sure you're logged in with: az login

   # Option 3: Use a connection string (not recommended for production)
   # ACS_CONNECTION_STRING=your_acs_connection_string_here

   # Option 4: Use an access key (not recommended for production)
   # ACS_ACCESS_KEY=your_acs_access_key
   
   # Sender information
   FROM_EMAIL_ADDRESS=DoNotReply@your-domain.azurecomm.net
   # OR use just the domain
   # FROM_SENDER_DOMAIN=your-domain.azurecomm.net

   # Recipients (comma-separated)
   TO_RECIPIENTS=recipient1@example.com,recipient2@example.com
   CC_RECIPIENTS=cc_recipient@example.com
   BCC_RECIPIENTS=bcc_recipient@example.com
   ```
   
   You can find your resource name, managed identity client ID, or other values in the Azure portal.

## Sample Applications

### Basic Email to Multiple Recipients

The `send_email.py` script demonstrates how to:
- Send emails to multiple recipients (To, CC, BCC)
- Use both plain text and HTML content
- Track email delivery status

To run:

```bash
uv run send_email.py
```

Before running, update the recipient email addresses in the `main()` function with your actual email addresses:

```python
# Sample email recipients - replace with actual email addresses
to_recipients = ["recipient1@example.com", "recipient2@example.com"]
cc_recipients = ["cc_recipient@example.com"]
bcc_recipients = ["bcc_recipient@example.com"]
```
## How It Works

These samples use the Azure Communication Services Email SDK to send emails. They retrieve necessary configuration values from environment variables or a .env file.

## Deployment Options

To deploy this app in different environments:

### Azure App Service with Managed Identity

1. Create a ZIP archive of the application:

   ```bash
   # Windows
   Compress-Archive -Path * -DestinationPath app.zip
   
   # Linux/Mac
   zip -r app.zip .
   ```

2. Deploy to App Service:

   ```bash
   az webapp deployment source config-zip -g <resource-group> -n <app-name> --src app.zip
   ```

3. Enable and configure managed identity:

   ```bash
   # Enable system-assigned managed identity
   az webapp identity assign -g <resource-group> -n <app-name>
   
   # OR enable user-assigned managed identity (recommended if deployed via azd)
   az webapp identity assign -g <resource-group> -n <app-name> --identities /subscriptions/<subscription-id>/resourcegroups/<resource-group>/providers/Microsoft.ManagedIdentity/userAssignedIdentities/<identity-name>
   
   # Assign the managed identity to the appropriate role for ACS
   az role assignment create --assignee-object-id <managed-identity-object-id> --assignee-principal-type ServicePrincipal --scope /subscriptions/<subscription-id>/resourceGroups/<resource-group>/providers/Microsoft.Communication/communicationServices/<acs-name> --role "Azure Communication Services SMTP Sender"
   ```

4. Configure environment variables in Azure portal or using Azure CLI:

   ```bash
   # For user-assigned identity (used by the azd deployment)
   az webapp config appsettings set -g <resource-group> -n <app-name> --settings ACS_NAME="<acs-name>" MANAGED_IDENTITY_CLIENT_ID="<managed-identity-client-id>" FROM_EMAIL_ADDRESS="<your-email-address>"
   
   # For system-assigned identity, omit the MANAGED_IDENTITY_CLIENT_ID
   az webapp config appsettings set -g <resource-group> -n <app-name> --settings ACS_NAME="<acs-name>" FROM_EMAIL_ADDRESS="<your-email-address>"
   ```

### Azure Container Apps with Managed Identity

1. Use the provided Dockerfile in this directory:

   ```
   FROM python:3.9-slim
   
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   COPY . .
   
   CMD ["python", "send_email.py"]
   ```

2. Build and push your container image:

   ```bash
   az acr build --registry <your-acr-name> --image email-app:latest .
   ```

3. Deploy to Azure Container Apps with managed identity:

   ```bash
   # Create user-assigned managed identity if not using the one from azd
   az identity create -g <resource-group> -n email-app-identity
   
   # Get the client ID of the identity
   identity_client_id=$(az identity show -g <resource-group> -n email-app-identity --query clientId -o tsv)
   identity_id=$(az identity show -g <resource-group> -n email-app-identity --query id -o tsv)
   
   # Deploy container app with managed identity
   az containerapp create \
     -n email-app \
     -g <resource-group> \
     --image <your-container-image> \
     --environment <container-apps-environment> \
     --user-assigned $identity_id \
     --env-vars ACS_NAME="<acs-name>" MANAGED_IDENTITY_CLIENT_ID="$identity_client_id" FROM_EMAIL_ADDRESS="<your-email-address>"
   
   # Assign role to the managed identity
   az role assignment create \
     --assignee-object-id "$(az identity show -g <resource-group> -n email-app-identity --query principalId -o tsv)" \
     --assignee-principal-type ServicePrincipal \
     --scope "/subscriptions/<subscription-id>/resourceGroups/<resource-group>/providers/Microsoft.Communication/communicationServices/<acs-name>" \
     --role "Azure Communication Services SMTP Sender"
   ```
   
   If you're using the managed identity created by azd, replace `email-app-identity` with the identity name from your azd deployment.

### Azure Functions

The code can be adapted to run as an Azure Function with HTTP triggers or timer triggers for scheduled emails.

## Additional Resources

- [Azure Communication Services Email Documentation](https://learn.microsoft.com/en-us/azure/communication-services/concepts/email/email-overview)
- [Python SDK Documentation](https://learn.microsoft.com/en-us/python/api/overview/azure/communication-email-readme?view=azure-python)
