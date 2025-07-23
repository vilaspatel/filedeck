# Content Manager Deployment Guide

This guide provides instructions for deploying the Content Manager application in various environments.

## Prerequisites

- Kubernetes cluster (v1.19+)
- Helm 3.x
- Docker (for building images)
- kubectl configured to access your cluster

## Quick Start

### 1. Build Docker Images

```bash
# Build backend image
cd backend
docker build -t content-manager/backend:1.0.0 .

# Build frontend image
cd ../frontend
docker build -t content-manager/frontend:1.0.0 .

# Push to your registry
docker tag content-manager/backend:1.0.0 your-registry/content-manager/backend:1.0.0
docker tag content-manager/frontend:1.0.0 your-registry/content-manager/frontend:1.0.0
docker push your-registry/content-manager/backend:1.0.0
docker push your-registry/content-manager/frontend:1.0.0
```

### 2. Create Secrets

```bash
# Create namespace
kubectl create namespace content-manager

# Create secrets for the application
kubectl create secret generic content-manager-secrets \
  --from-literal=secret-key=your-secret-key \
  --from-literal=database-url=postgresql://user:password@host:5432/db \
  -n content-manager

kubectl create secret generic azure-ad-secrets \
  --from-literal=tenant-id=your-tenant-id \
  --from-literal=client-id=your-client-id \
  --from-literal=client-secret=your-client-secret \
  --from-literal=authority=https://login.microsoftonline.com/your-tenant-id \
  -n content-manager

kubectl create secret generic storage-secrets \
  --from-literal=account-name=your-storage-account \
  --from-literal=account-key=your-storage-key \
  --from-literal=container-name=your-container \
  -n content-manager
```

### 3. Install with Helm

```bash
# Add Bitnami repository for dependencies
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

# Install the application
cd deployment
helm install content-manager ./helm-chart \
  --namespace content-manager \
  --set backend.image.registry=your-registry \
  --set frontend.image.registry=your-registry \
  --set ingress.hosts[0].host=your-domain.com
```

## Configuration

### Environment Variables

The application supports extensive configuration through environment variables. See the [values.yaml](../deployment/helm-chart/values.yaml) file for all available options.

### Storage Configuration

#### Azure Blob Storage
```yaml
backend:
  env:
    - name: STORAGE_TYPE
      value: "azure"
    - name: AZURE_STORAGE_ACCOUNT_NAME
      valueFrom:
        secretKeyRef:
          name: storage-secrets
          key: account-name
```

#### Google Cloud Storage
```yaml
backend:
  env:
    - name: STORAGE_TYPE
      value: "gcp"
    - name: GCP_PROJECT_ID
      value: "your-project-id"
```

#### AWS S3
```yaml
backend:
  env:
    - name: STORAGE_TYPE
      value: "aws"
    - name: AWS_REGION
      value: "us-east-1"
```

### Database Configuration

#### PostgreSQL (Recommended)
```yaml
postgresql:
  enabled: true
  auth:
    username: contentmanager
    password: changeme
    database: contentmanager
```

#### External Database
```yaml
postgresql:
  enabled: false

backend:
  secretEnv:
    - name: DATABASE_URL
      secretName: external-db-secret
      secretKey: database-url
```

### Azure AD Configuration

1. Register an application in Azure AD
2. Configure redirect URIs
3. Generate client secret
4. Update the secrets:

```bash
kubectl patch secret azure-ad-secrets \
  --patch='{"data":{"tenant-id":"'$(echo -n "your-tenant-id" | base64)'","client-id":"'$(echo -n "your-client-id" | base64)'","client-secret":"'$(echo -n "your-client-secret" | base64)'"}}' \
  -n content-manager
```

## Production Considerations

### Security

1. **Use strong secrets**: Generate cryptographically secure secrets
2. **Enable TLS**: Configure TLS certificates for HTTPS
3. **Network policies**: Implement Kubernetes network policies
4. **RBAC**: Configure proper service account permissions

### Monitoring

The application exposes Prometheus metrics on port 9090:

```yaml
monitoring:
  enabled: true
  serviceMonitor:
    enabled: true
```

### Backup

1. **Database backups**: Configure automated PostgreSQL backups
2. **File storage**: Ensure your cloud storage has backup/versioning enabled
3. **Configuration**: Backup Kubernetes manifests and Helm values

### Scaling

#### Horizontal Pod Autoscaling
```yaml
backend:
  autoscaling:
    enabled: true
    minReplicas: 2
    maxReplicas: 10
    targetCPUUtilizationPercentage: 70
```

#### Vertical Pod Autoscaling
Configure VPA for automatic resource adjustment:

```yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: content-manager-backend-vpa
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: content-manager-backend
  updatePolicy:
    updateMode: "Auto"
```

## Troubleshooting

### Common Issues

1. **Pod startup failures**: Check logs with `kubectl logs -f deployment/content-manager-backend`
2. **Database connection**: Verify database credentials and network connectivity
3. **Storage access**: Check storage account permissions and credentials
4. **Authentication**: Verify Azure AD configuration and redirect URIs

### Health Checks

The application provides health check endpoints:

- Backend: `GET /health` (basic), `GET /health/detailed` (comprehensive)
- Frontend: `GET /health` (nginx status)

### Logs

Access application logs:

```bash
# Backend logs
kubectl logs -f deployment/content-manager-backend -n content-manager

# Frontend logs
kubectl logs -f deployment/content-manager-frontend -n content-manager

# Database logs (if using included PostgreSQL)
kubectl logs -f statefulset/content-manager-postgresql -n content-manager
```

## Upgrading

### Application Updates

```bash
# Update images
helm upgrade content-manager ./helm-chart \
  --namespace content-manager \
  --set backend.image.tag=1.1.0 \
  --set frontend.image.tag=1.1.0
```

### Database Migrations

Database migrations are handled automatically on application startup. For manual migration:

```bash
kubectl exec -it deployment/content-manager-backend -- python -m alembic upgrade head
```

## Environment-Specific Deployments

### Development
```bash
helm install content-manager ./helm-chart \
  --namespace content-manager-dev \
  --values values-dev.yaml
```

### Staging
```bash
helm install content-manager ./helm-chart \
  --namespace content-manager-staging \
  --values values-staging.yaml
```

### Production
```bash
helm install content-manager ./helm-chart \
  --namespace content-manager-prod \
  --values values-prod.yaml
```

## Support

For deployment issues:

1. Check the [troubleshooting section](#troubleshooting)
2. Review application logs
3. Verify configuration values
4. Contact the development team 