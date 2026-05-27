# Mittari

Statistics demo service.


## Setup

Create a `.env` file in the project root (or set environment variables). Use `.env.example` as a template.
```

Required variables:

- LAJI_API_ACCESS_TOKEN: API access token for fetching data from api.laji.fi
- SECRET_KEY (required): Flask secret key used to sign sessions


### Run locally

```bash
docker compose up --build
```

Then open:

```text
http://localhost:8080
```

### Run in production (OpenShift)

The GitHub Actions workflow publishes images to:

```text
ghcr.io/luomus/mittari
```

Important: pushing to `main` automatically builds and pushes a new image to GHCR, but it does **not** automatically roll out OpenShift deployment.

#### One-time setup

1) Select the OpenShift project:

```bash
oc project mittari
```

2) Create GHCR pull secret (required if the image is private):

```bash
oc create secret docker-registry ghcr-pull-secret \
  --docker-server=ghcr.io \
  --docker-username=<github-username> \
  --docker-password=<github-token-with-read-packages> \
  --docker-email=<email> \
  --dry-run=client -o yaml | oc apply -f -
```

3) Create app resources from template:

```bash
oc process -f openshift/mittari-app.yaml | oc apply -f -
```

4) Sync runtime environment from local `.env` to OpenShift Secret + ConfigMap:

```bash
./scripts/sync-openshift-env.sh
```

5) Verify:

```bash
oc rollout status deployment/mittari
oc get pods
oc get route mittari
```

Open the HTTPS route URL in your browser.

#### Deploy future changes (normal workflow)

1) Push code changes to `main`:

```bash
git push origin main
```

2) Wait for GitHub Actions workflow `Build and Push Docker Image` to finish successfully.

3) Deploy newest image to OpenShift (this also syncs `.env` by default):

```bash
./scripts/deploy-openshift.sh
```

4) Verify rollout and running image:

```bash
oc rollout status deployment/mittari
oc get pods
oc get deployment mittari -o jsonpath='{.spec.template.spec.containers[0].image}{"\n"}'
```

#### Optional: deploy a specific image tag

```bash
IMAGE_TAG=main-0dff309 ./scripts/deploy-openshift.sh
```

#### Optional: update production secret values later

```bash
./scripts/sync-openshift-env.sh
oc rollout status deployment/mittari
```