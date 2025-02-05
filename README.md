# Distributed Rate Limiter

<!-- add a alert to the readme -->

<div style="background-color: #f8d7da; padding: 10px; border-radius: 5px;">
    <p style="color: #856404; font-weight: bold;">
        <strong>Warning:</strong> This is a proof-of-concept implementation and is not suitable for production environments.
    </p>
</div>


A scalable distributed rate limiter implementation using FastAPI, Redis Sentinel, and Docker. This system provides reliable rate limiting across multiple application instances with high availability through Redis master-slave replication and Sentinel monitoring.

## Overview

This project implements a distributed rate limiter that can handle requests across multiple application instances while maintaining consistent rate limiting through Redis. The system uses Redis Sentinel for high availability and Nginx for load balancing.

### Key Features

- Distributed rate limiting across multiple app instances
- High availability with Redis Sentinel (1 master, 2 slaves, 3 sentinels)
- Load balancing with Nginx
- Docker containerization for easy deployment
- Configurable rate limits via environment variables
- FastAPI-powered REST API endpoints

## Getting Started

### Prerequisites

- Docker
- Docker Compose

### Installation & Setup

1. Clone the repository:
```bash
git clone https://github.com/Rahulbeniwal26119/Distributed-Load-Balancer
cd distributed-rate-limiter
```

2. Start all services:
```bash
docker compose up -d
```

Optional: To start specific services
```bash
docker compose -f 'docker-compose.yml' up -d --build 'nginx'
```

This will start:
- 2 API instances (ports 8001, 8002)
- Redis master
- 2 Redis slaves
- 3 Redis sentinels
- Nginx load balancer (ports 80, 8000)

## Configuration

### Environment Variables

The application can be configured using the following environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| SENTINEL_HOSTS | Redis Sentinel hosts | sentinel-1:26379,sentinel-2:26379,sentinel-3:26379 |
| REDIS_MASTER | Redis master name | redis-master |
| REDIS_PASSWORD | Redis password | master |
| RATE_LIMIT | Max requests allowed | 10 |
| TIME_WINDOW | Time window in seconds | 60 |

### Rate Limiting Configuration

By default, the rate limiter allows:
- 10 requests per IP address
- Within a 60-second window
- Returns 429 (Too Many Requests) when exceeded

## API Endpoints

### Available Endpoints

| Endpoint | Description | Rate Limited |
|----------|-------------|--------------|
| GET / | Hello World endpoint | No |
| GET /limited_endpoint | Rate-limited test endpoint | Yes |
| GET /health | Health check endpoint | No |

### Testing the API

Access the API through:
```bash
# Load balanced endpoint
curl http://localhost:8000/

# Rate-limited endpoint
curl http://localhost:8000/limited_endpoint

# Health check
curl http://localhost:8000/health
```

## Architecture

### Components

1. **API Instances (app-1, app-2)**
   - FastAPI applications
   - Handle incoming HTTP requests
   - Implement rate limiting logic

2. **Redis Setup**
   - 1 master node (writes)
   - 2 slave nodes (reads)
   - 3 sentinel nodes (monitoring)

3. **Nginx Load Balancer**
   - Distributes traffic between API instances
   - Exposed on ports 80 and 8000

### High Availability

The Redis Sentinel configuration ensures:
- Automatic failover if master goes down
- High availability of the rate limiting service
- Consistent rate limiting across app instances

## Development

### Project Structure
```
.
├── docker-compose.yml    # Docker services configuration
├── Dockerfile           # Python application container
├── main.py             # FastAPI application code
├── sentinel.conf       # Redis Sentinel configuration
└── nginx.conf          # Nginx load balancer configuration
```

### Local Development

1. Install dependencies:
```bash
pip install -e .
```

2. Run locally:
```bash
uvicorn main:app --reload --port 8000
```

## Troubleshooting

### Common Issues

1. **Redis Connection Issues**
   - Verify Redis master and sentinels are running
   - Check sentinel configuration
   - Ensure network connectivity between containers

2. **Rate Limiting Issues**
   - Verify Redis connection
   - Check rate limit environment variables
   - Confirm network configuration

### Checking Service Status

```bash
# Check running containers
docker compose ps

# View logs
docker compose logs [service-name]
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- FastAPI for the web framework
- Redis for distributed caching
- Docker for containerization
