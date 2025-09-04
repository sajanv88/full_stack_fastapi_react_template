# FastAPI React App - Kubernetes Deployment

This Helm chart deploys a full-stack FastAPI React application to Kubernetes.

## Prerequisites

- Kubernetes 1.19+
- Helm 3.2.0+
- Docker registry access (public registry used by default)

## Installation

### 1. Update values.yaml

Edit `values.yaml` to configure:
- Docker image repository and tag
- Domain name for ingress
- Secret values (JWT, SMTP credentials)

### 2. Install the Chart

```bash
# Install with default values
helm install fastapi-react-app ./infra/helm

# Install with custom values
helm install fastapi-react-app ./infra/helm -f custom-values.yaml

# Install in specific namespace
kubectl create namespace fastapi-app
helm install fastapi-react-app ./infra/helm -n fastapi-app
```

### 3. Update Secrets

Before deploying, update the secrets in `templates/secret.yaml` or create them separately:

```bash
kubectl create secret generic app-secrets \
  --from-literal=jwt-secret="your-jwt-secret" \
  --from-literal=refresh-token-secret="your-refresh-secret" \
  --from-literal=smtp-user="your-email@gmail.com" \
  --from-literal=smtp-password="your-app-password" \
  --from-literal=smtp-mail-from="your-email@gmail.com"
```

## Configuration

### Key Values

| Parameter | Description | Default |
|-----------|-------------|---------|
| `image.repository` | Docker image repository | `sajanv88/fastapi-react-app` |
| `image.tag` | Docker image tag | `latest` |
| `replicaCount` | Number of replicas | `2` |
| `service.type` | Kubernetes service type | `ClusterIP` |
| `ingress.enabled` | Enable ingress | `true` |
| `ingress.hosts[0].host` | Domain name | `your-app.example.com` |
| `mongodb.enabled` | Deploy MongoDB | `true` |

### Environment Variables

The chart automatically configures:
- MongoDB connection
- JWT secrets
- SMTP configuration
- Base URL for frontend

## Features

✅ **Production Ready**
- Security contexts and non-root containers
- Resource limits and requests
- Health checks (liveness/readiness probes)
- Horizontal Pod Autoscaling (HPA)

✅ **Scalable**
- Multiple replicas with load balancing
- Autoscaling based on CPU/memory
- Persistent storage for MongoDB

✅ **Secure**
- Secrets management for sensitive data
- HTTPS with cert-manager integration
- Network policies ready

✅ **Observable**
- Health check endpoints
- Resource monitoring
- Structured logging

## Deployment Steps

### 1. Build and Push Docker Image

```bash
# Build the image
docker build -f backend/Dockerfile -t sajanv88/fastapi-react-app:v1.0.0 .

# Push to registry
docker push sajanv88/fastapi-react-app:v1.0.0
```

### 2. Deploy to Kubernetes

```bash
# Deploy with specific image tag
helm install fastapi-react-app ./infra/helm \
  --set image.tag=v1.0.0 \
  --set ingress.hosts[0].host=your-domain.com
```

### 3. Verify Deployment

```bash
# Check pods
kubectl get pods

# Check services
kubectl get svc

# Check ingress
kubectl get ingress

# View logs
kubectl logs -l app.kubernetes.io/name=fastapi-react-app
```

## Upgrade

```bash
# Upgrade with new image
helm upgrade fastapi-react-app ./infra/helm \
  --set image.tag=v1.1.0

# Upgrade with new values
helm upgrade fastapi-react-app ./infra/helm -f new-values.yaml
```

## Uninstall

```bash
helm uninstall fastapi-react-app
```

## Customization

### Custom Values File

Create `custom-values.yaml`:

```yaml
image:
  repository: your-registry/your-app
  tag: v1.0.0

ingress:
  hosts:
    - host: your-app.com
      paths:
        - path: /
          pathType: Prefix

resources:
  limits:
    cpu: 1000m
    memory: 1Gi
  requests:
    cpu: 500m
    memory: 512Mi

autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 20
```

### External MongoDB

To use external MongoDB, disable the built-in one:

```yaml
mongodb:
  enabled: false

env:
  - name: MONGO_URI
    value: "mongodb://external-mongo:27017"
```

## Monitoring

The application exposes health check endpoints:
- Liveness: `/api/v1/users/`
- Readiness: `/api/v1/users/`

Integrate with Prometheus for metrics collection.

## Support

For issues and questions, please check the application logs:

```bash
kubectl logs -l app.kubernetes.io/name=fastapi-react-app --tail=100
```
