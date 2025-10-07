# Azure Deployment Guide for Expense Prediction App

This guide provides step-by-step instructions for deploying the Expense Prediction application to Azure.

## Prerequisites

1. Azure account with active subscription
2. Azure CLI installed and configured
3. Docker installed locally

## Deployment Steps

### 1. Create Azure Resources

```powershell
# Login to Azure
az login

# Create a resource group
az group create --name ExpensePredictionRG --location eastus

# Create Azure Container Registry (ACR)
az acr create --resource-group ExpensePredictionRG --name expensepredictionacr --sku Basic

# Enable admin user for ACR
az acr update --name expensepredictionacr --admin-enabled true

# Get ACR credentials
az acr credential show --name expensepredictionacr
```

### 2. Build and Push Docker Image

```powershell
# Login to ACR
az acr login --name expensepredictionacr

# Build the Docker image
docker build -t expensepredictionapp:latest .

# Tag the image for ACR
docker tag expensepredictionapp:latest expensepredictionacr.azurecr.io/expensepredictionapp:latest

# Push the image to ACR
docker push expensepredictionacr.azurecr.io/expensepredictionapp:latest
```

### 3. Create and Configure App Service

```powershell
# Create App Service Plan
az appservice plan create --resource-group ExpensePredictionRG --name ExpensePredictionPlan --sku B1 --is-linux

# Create Web App for Containers
az webapp create --resource-group ExpensePredictionRG --plan ExpensePredictionPlan --name expense-prediction-app --deployment-container-image-name expensepredictionacr.azurecr.io/expensepredictionapp:latest

# Configure Web App to use ACR
az webapp config container set --name expense-prediction-app --resource-group ExpensePredictionRG --docker-custom-image-name expensepredictionacr.azurecr.io/expensepredictionapp:latest --docker-registry-server-url https://expensepredictionacr.azurecr.io --docker-registry-server-user expensepredictionacr --docker-registry-server-password <acr-password>
```

### 4. Configure Continuous Deployment (Optional)

1. Go to Azure DevOps and create a new project
2. Import your code repository
3. Create a new pipeline using the existing `azure-pipelines.yml` file
4. Configure pipeline variables:
   - `containerRegistry`: Your ACR name (e.g., expensepredictionacr)
   - `imageName`: Your image name (e.g., expensepredictionapp)
5. Run the pipeline

### 5. Access Your Application

Once deployed, your application will be available at:
```
https://expense-prediction-app.azurewebsites.net
```

## Troubleshooting

- **Container startup issues**: Check logs with `az webapp log tail --name expense-prediction-app --resource-group ExpensePredictionRG`
- **Deployment failures**: Review pipeline logs in Azure DevOps
- **Container registry access issues**: Verify ACR credentials and webapp configuration