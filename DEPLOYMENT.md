# OSRS GE API Deployment Guide

## Overview

The OSRS GE API runs as a Podman pod with three containers:
- **API container**: FastAPI application serving the REST API
- **Data fetcher container**: Background service that fetches OSRS item data every minute
- **News fetcher container**: Background service that aggregates news from OSRS blog and Reddit every 30 minutes

All containers share a mounted volume for SQLite databases.

## Prerequisites

- Podman installed on the host
- Access to pull images from `ghcr.io`
- Directory for SQLite database file

## Setup

### 1. Prepare the database directory

```bash
sudo mkdir -p /var/lib/osrs-ge/data
sudo chown $USER:$(id -gn) /var/lib/osrs-ge/data
# Optional: Copy existing item_data.db if you have one
# cp item_data.db /var/lib/osrs-ge/data/
```

### 2. Deploy with Podman

The pod is pre-configured to use `/var/lib/osrs-ge/data` for database storage.

```bash
# Pull the latest images
podman pull ghcr.io/fisherrjd/osrs_ge-api:latest
podman pull ghcr.io/fisherrjd/osrs_ge-fetcher:latest
podman pull ghcr.io/fisherrjd/osrs_ge-news:latest

# Create and start the pod
podman play kube pod.yaml
```

### 3. Verify deployment

```bash
# Check pod status
podman pod ps

# Check container logs
podman logs osrs_ge-api-api
podman logs osrs_ge-api-data-fetcher
podman logs osrs_ge-api-news-fetcher

# Test the API
curl http://localhost:8000/health
curl http://localhost:8000/api/items
curl http://localhost:8000/news
```

## Management

### Stop the pod
```bash
podman pod stop osrs_ge-api
```

### Start the pod
```bash
podman pod start osrs_ge-api
```

### Remove the pod
```bash
podman pod rm -f osrs_ge-api
```

### Update to latest images
```bash
# Pull new images
podman pull ghcr.io/fisherrjd/osrs_ge-api:latest
podman pull ghcr.io/fisherrjd/osrs_ge-fetcher:latest
podman pull ghcr.io/fisherrjd/osrs_ge-news:latest

# Recreate the pod
podman pod rm -f osrs_ge-api
podman play kube pod.yaml
```

### View logs
```bash
# Follow API logs
podman logs -f osrs_ge-api-api

# Follow data fetcher logs
podman logs -f osrs_ge-api-data-fetcher

# Follow news fetcher logs
podman logs -f osrs_ge-api-news-fetcher
```

## NixOS Integration

For NixOS, you can integrate this into your configuration. Example snippet:

```nix
{
  virtualisation.podman = {
    enable = true;
    dockerCompat = true;
  };

  systemd.services.osrs_ge-api = {
    description = "OSRS GE API Pod";
    after = [ "network.target" "podman.service" ];
    requires = [ "podman.service" ];
    wantedBy = [ "multi-user.target" ];

    serviceConfig = {
      Type = "oneshot";
      RemainAfterExit = "yes";
      ExecStartPre = [
        "${pkgs.podman}/bin/podman pull ghcr.io/fisherrjd/osrs_ge-api:latest"
        "${pkgs.podman}/bin/podman pull ghcr.io/fisherrjd/osrs_ge-fetcher:latest"
        "${pkgs.podman}/bin/podman pull ghcr.io/fisherrjd/osrs_ge-news:latest"
      ];
      ExecStart = "${pkgs.podman}/bin/podman play kube /path/to/osrs_ge/pod.yaml";
      ExecStop = "${pkgs.podman}/bin/podman pod stop osrs_ge-api";
    };
  };
}
```

## CI/CD

Images are automatically built and pushed to GitHub Container Registry on every push to `main`:
- API image: `ghcr.io/fisherrjd/osrs_ge-api:latest`
- Fetcher image: `ghcr.io/fisherrjd/osrs_ge-fetcher:latest`
- News image: `ghcr.io/fisherrjd/osrs_ge-news:latest`

### Enable GitHub Actions

1. Go to your repository settings
2. Navigate to Actions → General
3. Enable "Read and write permissions" for workflows
4. Push to `main` branch to trigger the build

## Troubleshooting

### Database not populated
If `/api/items` returns empty results:
- Check data fetcher logs: `podman logs osrs_ge-api-data-fetcher`
- Verify the database file exists in the mounted directory
- Ensure the fetcher has internet access to reach OSRS wiki APIs

### Port already in use
If port 8000 is already bound:
- Edit `pod.yaml` and change `hostPort: 8000` to another port
- Recreate the pod

### Permission denied on database
```bash
# Ensure the database directory is writable
sudo chown $USER:$USER /var/lib/osrs-ge/data
chmod 755 /var/lib/osrs-ge/data
```

## API Endpoints

- `GET /` - API info
- `GET /health` - Health check
- `GET /api/items` - List items with pagination and filtering
  - Query params: `skip`, `limit`, `members`, `min_volume`, `max_volume`, `min_price`, `max_price`, `name`, `sort_by`, `sort_order`
- `GET /news` - Get aggregated news from OSRS blog and Reddit, sorted by score

For full API documentation, visit `http://localhost:8000/docs` when the pod is running.
