# DevOps Lab 2: Containerized application and Kubernetes workflow

**Student:** Kartik Kumar  
**Roll number:** 2301730205  
**Email:** kartikjangra5366@gmail.com

## Scope and evidence note

The supplied material in this workspace was empty. The only lab specification available was the topic brief in the request. This project therefore implements that brief as four practicals: (1) Docker image/container lifecycle, (2) Kubernetes deployment and scaling, (3) rolling update and rollback, and (4) continuous deployment to Minikube. If your instructor provided a separate experiment list, compare it with these practicals before submitting.

Docker image build and container execution have been completed with Docker Desktop 29.8.1. Minikube 1.39.0 started a local Kubernetes 1.37.0 cluster; the app was deployed, scaled to four Ready Pods, updated to version 1.1.0, and rolled back successfully. The screenshots in `evidence/screenshots/` are captures of actual Windows PowerShell terminal windows running the displayed commands. The GitHub Actions workflow calls the tested reusable deployment script; the remote Actions job itself was not run because this workspace has no Git remote or registered self-hosted runner.

## Project layout

```text
app/server.py                  HTTP app and health endpoints
Dockerfile                     Small non-root Python image
k8s/namespace.yaml             Lab namespace
k8s/deployment.yaml            Two-replica Deployment and NodePort Service
.github/workflows/deploy.yml   Self-hosted Minikube CD workflow
scripts/verify.ps1             HTTP smoke checks
scripts/deploy.ps1             Reusable Minikube deployment / local CD script
evidence/                      Command output and actual PowerShell screenshots
reports/                       Four separate experiment PDFs
dist/                           Requested report and project ZIPs
```

## Requirements

- Python 3.10+ for local execution (the app uses only the standard library).
- Docker Desktop with its Linux engine running for image build/run.
- `kubectl` (included with Docker Desktop) and Minikube for Kubernetes practicals.
- A self-hosted GitHub Actions runner on the machine that can access the same Docker daemon and Minikube context for the included CD workflow.

The Python app has no third-party runtime dependencies. Install `requirements.txt` only if you want to regenerate PDFs or run the structural report validator.

## Run locally

```powershell
python .\app\server.py
```

In another PowerShell window:

```powershell
.\scripts\verify.ps1
```

The recorded in-process smoke test can also be rerun with `python .\scripts\smoke_test.py`. If PowerShell script invocation is restricted, run the equivalent checks directly:

```powershell
Invoke-RestMethod http://127.0.0.1:8080/healthz
Invoke-RestMethod http://127.0.0.1:8080/readyz
Invoke-RestMethod http://127.0.0.1:8080/api/info
```

## Docker image and container

With Docker Desktop's Linux engine running:

```powershell
docker build -t devops-lab2:1.0.0 .
docker image ls devops-lab2
docker run --rm -d --name devops-lab2 -p 8080:8080 devops-lab2:1.0.0
.\scripts\verify.ps1
docker logs devops-lab2
docker stop devops-lab2
```

The app listens on port 8080, exposes `/healthz` and `/readyz`, and returns identifying build information at `/api/info`.

## Kubernetes with Minikube

Minikube 1.39.0 and a local Kubernetes 1.37.0 cluster are installed and started on the preparation machine. For a fresh Windows setup, use `winget install Kubernetes.minikube` or download the official Windows binary from the [Minikube start guide](https://minikube.sigs.k8s.io/docs/start/). Docker Desktop supplies `kubectl` and the Linux container engine. Start the local cluster with:

```powershell
minikube start --driver=docker
kubectl get nodes
docker build -t devops-lab2:1.0.0 .
minikube image load devops-lab2:1.0.0
kubectl apply -f .\k8s\namespace.yaml
kubectl apply -f .\k8s\deployment.yaml
kubectl -n devops-lab2 rollout status deployment/devops-lab2
kubectl -n devops-lab2 get pods,svc
minikube service devops-lab2 -n devops-lab2 --url
```

Scale to four replicas and verify:

```powershell
kubectl -n devops-lab2 scale deployment/devops-lab2 --replicas=4
kubectl -n devops-lab2 get deployment,pods
```

## Rolling update and rollback

Build/load a new tagged image, then update both the pod image and reported version:

```powershell
docker build -t devops-lab2:1.1.0 .
minikube image load devops-lab2:1.1.0
kubectl -n devops-lab2 set image deployment/devops-lab2 web=devops-lab2:1.1.0
kubectl -n devops-lab2 set env deployment/devops-lab2 APP_VERSION=1.1.0
kubectl -n devops-lab2 rollout status deployment/devops-lab2
kubectl -n devops-lab2 rollout history deployment/devops-lab2
```

Rollback the last revision and wait for it to finish:

```powershell
kubectl -n devops-lab2 rollout undo deployment/devops-lab2
kubectl -n devops-lab2 rollout status deployment/devops-lab2
```

## Continuous deployment

Run the local deployment automation with an immutable tag:

```powershell
pwsh -NoLogo -NoProfile -File .\scripts\deploy.ps1 -ImageTag lab2-demo-001
```

`.github/workflows/deploy.yml` invokes the same tested script with the commit SHA. It targets a **self-hosted** runner because a GitHub-hosted runner cannot reach Minikube on a student's workstation. Configure that runner with Docker, Minikube and kubectl, and connect the project to GitHub before enabling pushes.

## Reports and archives

The four PDFs are in `reports/`. `dist/devops-lab2-reports.zip` bundles the reports; `dist/devops-lab2-project.zip` bundles the complete project including evidence and reports. Reports distinguish verified local deployment from the GitHub Actions job, which needs a remote and runner.

## Verification

Run `.\scripts\verify.ps1` while the local app is running. Reproduce the container capture with `pwsh -NoLogo -NoProfile -File .\scripts\run-powershell-capture.ps1 -Experiment docker-run`; deploy to Minikube with `pwsh -NoLogo -NoProfile -File .\scripts\deploy.ps1 -ImageTag demo-001`. Capture scripts open a real PowerShell window, run the selected commands, and save a PNG from that window. The GitHub-hosted Actions job remains pending the repository remote and self-hosted runner setup.
