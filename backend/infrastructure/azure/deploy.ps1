# Azure Infrastructure Deployment Script
param(
    [Parameter(Mandatory=$true)]
    [string]$Environment,
    
    [Parameter(Mandatory=$false)]
    [string]$Location = "East US",
    
    [Parameter(Mandatory=$false)]
    [string]$ResourceGroupName = "lda-backend-rg"
)

Write-Host "Deploying LDA Backend Infrastructure to Azure..." -ForegroundColor Green

# Create resource group if it doesn't exist
Write-Host "Creating/verifying resource group: $ResourceGroupName" -ForegroundColor Yellow
az group create --name $ResourceGroupName --location $Location

# Deploy infrastructure
Write-Host "Deploying infrastructure for environment: $Environment" -ForegroundColor Yellow
az deployment group create `
    --resource-group $ResourceGroupName `
    --template-file "main.bicep" `
    --parameters environment=$Environment location=$Location resourceGroupName=$ResourceGroupName

Write-Host "Infrastructure deployment completed!" -ForegroundColor Green

# Get outputs
Write-Host "Retrieving deployment outputs..." -ForegroundColor Yellow
$outputs = az deployment group show --resource-group $ResourceGroupName --name main --query properties.outputs

Write-Host "Deployment Outputs:" -ForegroundColor Cyan
Write-Host $outputs 