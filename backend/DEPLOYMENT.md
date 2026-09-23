# Deploying the QuoteBind Backend to Azure Container Apps

Exact steps used for the actual deployment. Image is built in Azure via
`az acr build` — no local Docker required.

**Live:** `<backend-fqdn>` (printed by step 10; not committed here — see the note in step 9 on why)

This is the `backend/` project within the QuoteBind repo — a sibling to
`frontend/`, deployed separately to Azure Static Web Apps (see
`../frontend/DEPLOYMENT.md`). That deployment needs this backend's FQDN,
and this backend's CORS config (step 9) needs the frontend's hostname
added to it — the two docs cross-reference each other at that point. All
commands below are run from inside `backend/` unless noted otherwise.

## Prerequisites

- Azure CLI (`az`) installed and logged in: `az login`
- On Windows PowerShell, set UTF-8 output first (avoids a console-encoding crash during `az acr build`'s log streaming):
  ```powershell
  chcp 65001
  [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
  ```

## 1. `Dockerfile` (`backend/`)

```dockerfile
FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 2. `.dockerignore` (`backend/`)

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

No `frontend/` exclusion needed here anymore — now that the backend lives
in its own `backend/` folder and the build context (step 7) is scoped to
just that folder, the frontend project (and its huge `node_modules`) is
never even part of the context in the first place. Previously, when
`Dockerfile` lived at the repo root and the build context was the whole
repo, this bit us for real: `az acr build`'s local tar-packing step took
several minutes just walking `node_modules`'s huge file count before
failing/timing out, even though none of it ended up in the image. Scoping
the build context is a more direct fix than excluding it after the fact.

## 3. Variables

```powershell
$RG = "quotebind-rg"
$LOCATION = "eastus"
$PG_LOCATION = "eastus2"
$CAE_LOCATION = "eastus2"
$ACR_NAME = "quotebindacr<unique-suffix>"   # globally unique, alphanumeric only
$PG_SERVER = "<pg-server-name>"
$PG_ADMIN_USER = "<pg-admin-username>"
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

Connection string (used in step 10):
```
postgresql://<PG_ADMIN_USER>:<PG_ADMIN_PASSWORD>@<PG_SERVER>.postgres.database.azure.com:5432/<PG_DB_NAME>?sslmode=require
```

## 6. Container Registry

```powershell
az acr create --resource-group $RG --name $ACR_NAME --sku Basic
```

## 7. Build the image

Run from the repo root, with `backend/` as the build context (equivalently: `cd backend` first and use `.` as the context):
```powershell
az acr build --registry $ACR_NAME --image quotebind-api:latest ./backend
```

Verify it actually built (the CLI can report a false failure from its own log-streaming, independent of the build):
```powershell
az acr task list-runs --registry $ACR_NAME --top 1 -o table
```

If a build hangs at "Packing source code into tar to upload..." for more
than a few seconds, double-check the build context is actually `backend/`
and not the repo root (see step 2's note on why that matters) before
assuming something is actually wrong.

## 8. Container Apps environment

```powershell
az containerapp env create --resource-group $RG --name $CAE_NAME --location $CAE_LOCATION
```

If this fails, delete before retrying the same name:
```powershell
az containerapp env delete --resource-group $RG --name $CAE_NAME --yes
```

## 9. CORS

`main.py` allows the local Vite dev server by default, plus whatever's in
the `CORS_ALLOWED_ORIGINS` env var (comma-separated) — deployment-specific
origins (like the deployed frontend's hostname) are deliberately **not**
hardcoded in source, so they don't end up committed to git:

```python
extra_cors_origins = [
    origin.strip()
    for origin in os.environ.get("CORS_ALLOWED_ORIGINS", "").split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", *extra_cors_origins],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type"],
)
```

Set the frontend's Static Web App hostname (created in
`../frontend/DEPLOYMENT.md`) via this env var when deploying (step 10). To
change it later, **no image rebuild needed** — just update the env var on
the running Container App:
```powershell
az containerapp update --resource-group $RG --name $CA_NAME `
  --set-env-vars CORS_ALLOWED_ORIGINS="https://<swa-hostname>"
```

## 10. Deploy the container app

First deploy (creates the app):
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
  --env-vars DATABASE_URL=secretref:database-url "CORS_ALLOWED_ORIGINS=https://<swa-hostname>" `
  --query properties.configuration.ingress.fqdn
```

`--registry-identity system` authenticates the pull via the app's own managed identity (auto-granted `AcrPull`) — no registry password involved. If the frontend isn't deployed yet, omit `CORS_ALLOWED_ORIGINS` for now and set it later with the `az containerapp update --set-env-vars` command in step 9 — no rebuild needed for that.

Subsequent redeploys after rebuilding the image (an actual code change) —
same image tag, so this forces the Container App onto the freshly built
image:
```powershell
az containerapp update `
  --resource-group $RG `
  --name $CA_NAME `
  --image "$ACR_NAME.azurecr.io/quotebind-api:latest"
```

> **Note:** this doesn't create a new *named* revision — Container Apps
> dedupes identical specs, and since the tag string (`:latest`) is
> unchanged, `az containerapp revision list` still shows the same revision
> name as before. It does restart the replica and re-pull the tag, so the
> new code genuinely goes live — just don't use "a new revision appeared"
> as your signal that the redeploy worked. Verify actual behavior instead
> (step 11).

## 11. Verify

```powershell
curl "https://<fqdn>/"           # {"message":"Get Successful!"}
curl "https://<fqdn>/products/"  # [] on a fresh DB — confirms DB connectivity
az containerapp logs show --resource-group $RG --name $CA_NAME --follow
```

```powershell
az containerapp revision list --resource-group $RG --name $CA_NAME `
  --query "[].{name:name, active:properties.active, runningState:properties.runningState, healthState:properties.healthState}"
```

To verify a CORS config change specifically, see `../frontend/DEPLOYMENT.md`
step 6 (a plain `curl` GET won't reveal CORS problems — browsers enforce
CORS, not the server response alone).

Confirmed working after the `backend/` restructure (2026-09-23): rebuilt
with the new scoped context (78.8 KiB vs. minutes of hanging before — see
step 2), redeployed, `curl .../` returned `200`, and a CORS preflight with
the deployed frontend's `Origin` header returned the correct
`access-control-allow-origin`. Re-confirmed after moving CORS origins to
`CORS_ALLOWED_ORIGINS` (2026-09-24): rebuilt, redeployed with the env var
set, same two checks passed again.

## Out of scope

- CI/CD pipeline
- Custom domain / managed SSL certificate
- Tightening the Postgres firewall rule beyond "allow all" (step 5 uses a broad range for simplicity)
- Single-container deployment (serving the built frontend from this same
  image, rather than a separate Static Web App) — considered and
  deliberately not used for this deployment. Trade-offs: one container/URL
  and no CORS to manage, at the cost of the frontend and backend no longer
  deploying or scaling independently, and losing CDN-backed static asset
  serving.
