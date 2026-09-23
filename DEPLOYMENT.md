# Deploying QuoteBind to Azure Container Apps

Exact steps used for the actual deployment (2026-09-22). Image is built in Azure via `az acr build` — no local Docker required.

## Prerequisites

- Azure CLI (`az`) installed and logged in: `az login`
- On Windows PowerShell, set UTF-8 output first (avoids a console-encoding crash during the image build log streaming):
  ```powershell
  chcp 65001
  [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
  ```

## 1. `Dockerfile` (repo root)

```dockerfile
FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 2. `.dockerignore` (repo root)

```
.venv/
__pycache__/
*.pyc
.git/
.gitignore
.env.local
app.log
.pytest_cache/
.mypy_cache/
.coverage
README.md
```

## 3. Variables

```powershell
$RG = "quotebind-rg"
$LOCATION = "eastus"
$PG_LOCATION = "eastus2"
$CAE_LOCATION = "eastus2"
$ACR_NAME = "quotebindacr<unique-suffix>"   # globally unique, alphanumeric only
$PG_SERVER = "quotebind-pg"
$PG_ADMIN_USER = "quotebindadmin"
$PG_ADMIN_PASSWORD = "<strong-password>"
$PG_DB_NAME = "QuoteBindAdmin"
$CAE_NAME = "quotebind-env"
$CA_NAME = "quotebind-api"
```

`$PG_LOCATION` / `$CAE_LOCATION` differ from `$LOCATION`: Postgres and the Container Apps environment both failed to provision in `eastus` on this subscription (region capacity/policy restrictions) and succeeded in `eastus2`. A resource's region doesn't need to match its resource group's region.

## 4. Resource group

```powershell
az group create --name $RG --location $LOCATION
```

## 5. Postgres

```powershell
az postgres flexible-server create `
  --resource-group $RG `
  --name $PG_SERVER `
  --location $PG_LOCATION `
  --admin-user $PG_ADMIN_USER `
  --admin-password $PG_ADMIN_PASSWORD `
  --sku-name Standard_B1ms `
  --tier Burstable `
  --version 16 `
  --storage-size 32 `
  --public-access 0.0.0.0-255.255.255.255 `
  --yes

az postgres flexible-server db create `
  --resource-group $RG `
  --server-name $PG_SERVER `
  --name $PG_DB_NAME
```

Connection string (used in step 9):
```
postgresql://<PG_ADMIN_USER>:<PG_ADMIN_PASSWORD>@<PG_SERVER>.postgres.database.azure.com:5432/<PG_DB_NAME>?sslmode=require
```

## 6. Container Registry

```powershell
az acr create --resource-group $RG --name $ACR_NAME --sku Basic
```

## 7. Build the image

```powershell
az acr build --registry $ACR_NAME --image quotebind-api:latest .
```

Verify it actually built (the CLI can report a false failure from its own log-streaming, independent of the build):
```powershell
az acr task list-runs --registry $ACR_NAME --top 1 -o table
```

## 8. Container Apps environment

```powershell
az containerapp env create --resource-group $RG --name $CAE_NAME --location $CAE_LOCATION
```

If this fails, delete before retrying the same name:
```powershell
az containerapp env delete --resource-group $RG --name $CAE_NAME --yes
```

## 9. Deploy the container app

```powershell
az containerapp create `
  --resource-group $RG `
  --name $CA_NAME `
  --environment $CAE_NAME `
  --image "$ACR_NAME.azurecr.io/quotebind-api:latest" `
  --registry-server "$ACR_NAME.azurecr.io" `
  --registry-identity system `
  --target-port 8000 `
  --ingress external `
  --secrets database-url="postgresql://$PG_ADMIN_USER:$PG_ADMIN_PASSWORD@$PG_SERVER.postgres.database.azure.com:5432/${PG_DB_NAME}?sslmode=require" `
  --env-vars DATABASE_URL=secretref:database-url `
  --query properties.configuration.ingress.fqdn
```

`--registry-identity system` authenticates the pull via the app's own managed identity (auto-granted `AcrPull`) — no registry password involved.

Prints the app's public FQDN.

## 10. Verify

```powershell
curl "https://<fqdn>/"           # {"message":"Get Successful!"}
curl "https://<fqdn>/products/"  # [] on a fresh DB — confirms DB connectivity
az containerapp logs show --resource-group $RG --name $CA_NAME --follow
```

```powershell
az containerapp revision list --resource-group $RG --name $CA_NAME `
  --query "[].{name:name, active:properties.active, runningState:properties.runningState, healthState:properties.healthState}"
```

## Out of scope

- CI/CD pipeline
- Custom domain / managed SSL certificate
- Tightening the Postgres firewall rule beyond "allow all" (step 5 uses a broad range for simplicity)
