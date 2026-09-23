# Deploying the QuoteBind Frontend to Azure Static Web Apps

Exact steps used for the actual deployment. Deployed directly via the SWA
CLI from a local production build — see "Out of scope" below for why this
isn't wired to CI/CD (yet).

**Live:** `<swa-hostname>` (printed by step 3; not committed here — see the note in step 2)

The backend lives in a sibling `backend/` project, deployed to its own
Container App — see `../backend/DEPLOYMENT.md` for its deployment. This
frontend needs that backend's URL (step 2) and, for the backend to
actually accept requests from this site, needs its own hostname added to
the backend's CORS allow-list (`../backend/main.py`) — see the note in
step 3.

## Prerequisites

- Azure CLI (`az`) installed and logged in: `az login`
- Node.js / npm
- The backend already deployed (its FQDN is needed in step 2)

## 1. Variables

```powershell
$RG = "quotebind-rg"          # same resource group as the backend
$SWA_NAME = "quotebind-frontend"
$SWA_LOCATION = "eastus2"     # Static Web Apps is only available in a handful of regions — see `az staticwebapp create --help`
```

## 2. Point the production build at the deployed backend

Create `.env.production` (repo root of this frontend project — Vite loads
it automatically for `vite build`). It's gitignored, not committed — the
backend's FQDN is a real, live URL, and Vite bakes whatever's in here
directly into the public JS bundle at build time regardless (anyone can
read it out of the deployed site's network requests), so there's no
reason to also carry it in git history:
```
VITE_API_BASE_URL=https://<backend-fqdn>
```

This file has to exist *before* step 4's build, and changing it means
rebuilding.

## 3. Create the Static Web App

```powershell
az staticwebapp create --name $SWA_NAME --resource-group $RG --location $SWA_LOCATION --sku Free
az staticwebapp show --name $SWA_NAME --resource-group $RG --query defaultHostname -o tsv
```

Take the printed hostname (a random name under `*.azurestaticapps.net`).

> **Backend CORS step (do this before step 6's verification, not before
> deploying the frontend itself):** set `https://<that-hostname>` in the
> backend's `CORS_ALLOWED_ORIGINS` env var (see `../backend/DEPLOYMENT.md`
> step 9) — no rebuild needed, just `az containerapp update
> --set-env-vars`. Without this, the deployed frontend loads fine but
> every API call fails in the browser with a CORS error — `curl` won't
> show this, since CORS is enforced by the browser, not the server
> response alone.

## 4. Build

```powershell
npm run build
```

Sanity-check the production API URL actually got baked into the bundle:
```powershell
Select-String -Path dist/assets/*.js -Pattern "azurecontainerapps.io"
```

## 5. Deploy

```powershell
$SWA_TOKEN = az staticwebapp secrets list --name $SWA_NAME --resource-group $RG --query "properties.apiKey" -o tsv
npx --yes @azure/static-web-apps-cli deploy ./dist --deployment-token $SWA_TOKEN --env production
```

> **Secret handling:** `$SWA_TOKEN` is a deployment credential (grants push
> access to this Static Web App) — avoid printing it to a shared
> terminal/log. Rotate it via `az staticwebapp secrets reset-api-key` if it
> leaks.

## 6. Verify

```powershell
curl "https://<swa-hostname>/"   # 200, serves index.html
```

Open it in a browser and confirm the Quotes grid actually loads data from
the backend (not just that the page renders). If it doesn't, check the
browser console for a CORS error first (see step 3's note) before assuming
the frontend itself is broken.

`curl` can't verify CORS itself (browsers enforce it), but a preflight
request with the frontend's `Origin` header shows whether the backend
*would* allow it:
```powershell
curl -i -X OPTIONS "https://<backend-fqdn>/quotes/" `
  -H "Origin: https://<swa-hostname>" `
  -H "Access-Control-Request-Method: GET"
# look for: access-control-allow-origin: https://<swa-hostname>
```

Confirmed working (2026-09-23): the preflight above returned the correct
`access-control-allow-origin` for the deployed frontend's hostname, and a
plain `curl` on the frontend's own URL returned `200` with `index.html`.
The Quotes grid itself shows "No rows" — expected, since the backend's
Azure Postgres instance had not been seeded yet at that point; the
frontend↔backend wiring is correct, there's just no data. Re-confirmed
after the `backend/` restructure (same day): redeployed this frontend
build (nothing here actually changed, since only the backend moved) and
re-ran both checks — same results.

## Out of scope

- CI/CD pipeline — Static Web Apps' native GitHub Actions integration
  (`az staticwebapp create --source <repo> --branch <branch> ...`) would
  replace step 5 with an automatic build+deploy on every push. Not set up
  here; that flow also requires an interactive GitHub authorization this
  session can't drive — deploys are manual via the SWA CLI for now.
- Custom domain / managed SSL certificate
- Single-container deployment (serving this build from the FastAPI backend
  itself instead of Static Web Apps) — considered and deliberately not
  used for this deployment; see `../backend/DEPLOYMENT.md`'s intro if
  revisiting that trade-off
