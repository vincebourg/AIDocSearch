# Kubernetes Deployment Guide for AIDocSearch

This guide provides quick-start instructions for deploying AIDocSearch on Minikube with development mode and hot-reload capabilities.

For the full detailed plan including troubleshooting, verification steps, and production considerations, see: `C:\Users\vince\.claude\plans\iterative-watching-quasar.md`

## Prerequisites

- Minikube installed and running
- kubectl configured
- Docker Desktop running
- Milvus running on host Docker (port 19530)
- OpenAI API key
- Project directory: `C:\Users\vince\source\repos\AIDocSearch`

## Quick Start

### 1. Start Minikube

```powershell
# Start with sufficient resources
minikube start --cpus=4 --memory=4096 --driver=docker

# Verify cluster is ready
kubectl cluster-info
kubectl get nodes
```

### 2. Start Milvus on Host

```powershell
# Windows
.\standalone_embed.bat start

# Verify Milvus is accessible
curl http://localhost:19530/healthz
```

### 3. Setup Hot-Reload Mount

```powershell
# Run in a separate PowerShell terminal and keep it open
minikube mount C:\Users\vince\source\repos\AIDocSearch:/mnt/aidocsearch
```

**Important**: Keep this terminal running throughout your development session.

### 4. Build Docker Images

```powershell
# Navigate to project directory
cd C:\Users\vince\source\repos\AIDocSearch

# Configure Docker to use Minikube's daemon
& minikube -p minikube docker-env --shell powershell | Invoke-Expression

# Build images
docker build -t aidocsearch-server:dev -f Dockerfile.server .
docker build -t aidocsearch-app:dev -f Dockerfile.app .

# Verify images are in Minikube
docker images | Select-String aidocsearch
```

### 5. Create Namespace and ConfigMap

```bash
# Create namespace
kubectl create namespace aidocsearch

# Set as default namespace
kubectl config set-context --current --namespace=aidocsearch

# Apply ConfigMap
kubectl apply -f k8s/configmap.yaml
```

### 6. Create Secret for OpenAI API Key

```powershell
# Replace with your actual API key
$OPENAI_KEY = "sk-proj-your-key-here"

kubectl create secret generic aidocsearch-secrets `
  --from-literal=OPENAI_API_KEY=$OPENAI_KEY `
  -n aidocsearch

# Verify secret was created
kubectl get secrets -n aidocsearch
```

### 7. Deploy All Resources

```bash
# Apply all Kubernetes manifests
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/pvc-data.yaml
kubectl apply -f k8s/pvc-uploads.yaml
kubectl apply -f k8s/server-deployment.yaml
kubectl apply -f k8s/server-service.yaml
kubectl apply -f k8s/app-deployment.yaml
kubectl apply -f k8s/app-service.yaml

# Or apply all at once
kubectl apply -f k8s/
```

### 8. Wait for Pods to Start

```bash
# Watch pods come up
kubectl get pods -n aidocsearch -w

# Check logs
kubectl logs -f deployment/aidocsearch-server -n aidocsearch
```

### 9. Populate Data Directory

```bash
# Get server pod name
kubectl get pods -n aidocsearch -l app=aidocsearch,component=server

# Copy data directory (one-time setup)
kubectl cp C:\Users\vince\source\repos\AIDocSearch\data `
  <server-pod-name>:/app/data -n aidocsearch

# Restart server to trigger indexing
kubectl rollout restart deployment/aidocsearch-server -n aidocsearch

# Watch indexing logs
kubectl logs -f deployment/aidocsearch-server -n aidocsearch
```

### 10. Access the Application

```bash
# Option 1: Get Minikube IP and open browser
minikube ip
# Then open: http://<minikube-ip>:30850

# Option 2: Use Minikube service command (recommended - auto-opens browser)
minikube service aidocsearch-app -n aidocsearch

# Option 3: Port forward to localhost
kubectl port-forward service/aidocsearch-app 8501:8501 -n aidocsearch
# Then open: http://localhost:8501
```

## Verify Deployment

### Check All Resources

```bash
kubectl get all -n aidocsearch
```

Expected output:
- 2 pods (server, app) in Running state
- 2 services (server ClusterIP, app NodePort)
- 2 deployments
- 2 PVCs in Bound state

### Test Server Health

```bash
kubectl exec deployment/aidocsearch-server -n aidocsearch -- \
  curl -s http://localhost:5000/health
```

Expected: `{"status":"healthy","vector_store_ready":true,"documents_indexed":6}`

### Test Milvus Connection

```bash
kubectl logs deployment/aidocsearch-server -n aidocsearch | grep -i milvus
```

Expected: "Connected to Milvus at http://host.minikube.internal:19530"

### Test End-to-End

1. Open Streamlit UI in browser
2. Enter question: "Quels sont les contentieux en cours?"
3. Verify response is generated
4. Navigate to document upload page
5. Upload a test .txt file
6. Verify success message

### Test Hot-Reload

1. Edit `app.py` on your host machine
2. Change the title from "Bot Assistant Droit des affaires" to "Bot TEST"
3. Wait 5-10 seconds
4. Refresh browser
5. New title should appear (no rebuild needed!)

## Development Workflow

### Daily Development

```bash
# 1. Start Minikube and Milvus
minikube start
.\standalone_embed.bat start

# 2. Start mount (separate terminal)
minikube mount C:\Users\vince\source\repos\AIDocSearch:/mnt/aidocsearch

# 3. Verify pods are running
kubectl get pods -n aidocsearch

# 4. Make code changes on host
# 5. Changes automatically reload
# 6. Test in browser
```

### View Logs

```bash
# Server logs
kubectl logs -f deployment/aidocsearch-server -n aidocsearch

# App logs
kubectl logs -f deployment/aidocsearch-app -n aidocsearch
```

### When to Rebuild Images

Only rebuild if you:
- Install new Python packages
- Modify Dockerfile
- Change baked-in environment variables

```bash
# Rebuild and restart
eval $(minikube docker-env)
docker build -t aidocsearch-server:dev -f Dockerfile.server .
kubectl rollout restart deployment/aidocsearch-server -n aidocsearch
```

## Troubleshooting

### Server Cannot Connect to Milvus

```bash
# Test from Minikube
minikube ssh
curl http://host.minikube.internal:19530/healthz
exit

# Check Milvus on host
netstat -an | findstr 19530

# If needed, use host IP instead
# Get host IP: ipconfig | findstr IPv4
# Update ConfigMap with: kubectl edit configmap aidocsearch-config -n aidocsearch
# Change MILVUS_URI to http://<your-ip>:19530
```

### Images Not Found

```bash
# Verify images are in Minikube
eval $(minikube docker-env)
docker images | grep aidocsearch

# Check deployment
kubectl describe pod <pod-name> -n aidocsearch
```

### Hot-Reload Not Working

```bash
# Verify mount is active (check mount terminal)
# Verify mount inside Minikube
minikube ssh
ls -la /mnt/aidocsearch
exit

# Force restart
kubectl rollout restart deployment/aidocsearch-server -n aidocsearch
```

### Cannot Access UI

```bash
# Use Minikube service helper
minikube service aidocsearch-app -n aidocsearch

# Or try port-forward
kubectl port-forward service/aidocsearch-app 8501:8501 -n aidocsearch
```

## Clean Up

```bash
# Delete namespace (removes all resources)
kubectl delete namespace aidocsearch

# Or delete individual resources
kubectl delete -f k8s/

# Stop Minikube (preserves state)
minikube stop

# Delete Minikube cluster completely
minikube delete
```

## Architecture

```
Browser
  |
  | (NodePort 30850)
  v
Streamlit App Pod (aidocsearch-app)
  |
  | (ClusterIP)
  v
Flask Server Pod (aidocsearch-server)
  |
  | (host.minikube.internal:19530)
  v
Milvus (Host Docker)
  |
  | (OpenAI API)
  v
OpenAI Embeddings & Chat
```

## Key Files

- `k8s/namespace.yaml` - Namespace isolation
- `k8s/configmap.yaml` - Configuration (Milvus URI, models)
- `k8s/pvc-data.yaml` - Persistent storage for documents
- `k8s/pvc-uploads.yaml` - Persistent storage for uploads
- `k8s/server-deployment.yaml` - Flask backend deployment
- `k8s/server-service.yaml` - Internal service for backend
- `k8s/app-deployment.yaml` - Streamlit frontend deployment
- `k8s/app-service.yaml` - External service for frontend

## Success Criteria

Deployment is successful when:

1. All pods are Running and Ready
2. Server connects to Milvus on host
3. Documents are indexed successfully
4. Streamlit UI accessible from browser
5. Chat functionality works end-to-end
6. Document upload works
7. Hot-reload works (code changes without rebuild)
8. Health checks passing
9. No errors in logs

## Next Steps

- Test chat with various questions
- Upload new documents
- Monitor resource usage: `kubectl top pods -n aidocsearch`
- Iterate on code with hot-reload
- Consider production deployment plan

## Full Documentation

For detailed troubleshooting, verification steps, and production considerations, see the full plan at:
`C:\Users\vince\.claude\plans\iterative-watching-quasar.md`
