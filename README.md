# Starlink Dashboard

Monitor your Starlink dish with either a simple web dashboard or a full Prometheus/Grafana stack.

## Option 1: Prometheus + Grafana Stack (Recommended)

A complete monitoring solution with historical data, customizable dashboards, and alerting.

### Features
- **90 days** of historical data retention
- **Pre-configured Grafana dashboard** with throughput, latency, SNR, obstructions, alerts
- **Prometheus metrics** for custom queries and alerting
- Uses [starlink-grpc-tools](https://github.com/sparky8512/starlink-grpc-tools) exporter

### Quick Start

```bash
docker compose up -d
```

Access:
- **Grafana**: http://localhost:3000 (admin / starlink)
- **Prometheus**: http://localhost:9090

### Architecture

```
┌─────────────────┐     ┌─────────────┐     ┌─────────────┐
│  Starlink Dish  │────▶│  Exporter   │────▶│ Prometheus  │
│  192.168.100.1  │     │  (gRPC)     │     │  (TSDB)     │
└─────────────────┘     └─────────────┘     └──────┬──────┘
                                                   │
                                            ┌──────▼──────┐
                                            │   Grafana   │
                                            │  Dashboard  │
                                            └─────────────┘
```

### Ports

| Service | Port |
|---------|------|
| Grafana | 3000 |
| Prometheus | 9090 |
| Starlink Exporter | 9817 |

---

## Option 2: Simple Web Dashboard

A lightweight, real-time dashboard with no historical data storage.

![Dashboard Screenshot](./screenshot.png)

### Features
- **Real-time metrics**: Latency, download/upload speeds, power consumption
- **Visual sparklines**: 60-second history graphs
- **Connection status**: State, uptime, drop rate, SNR quality
- **Auto-refresh**: Updates every 5 seconds

### Quick Start

```bash
docker build -t starlink-dashboard .
docker run -d --name starlink-simple --network host starlink-dashboard
```

Access: http://localhost:8100

---

## Requirements

- Docker and Docker Compose
- Network access to Starlink dish (192.168.100.1)

## License

MIT License - see [LICENSE](LICENSE)

## Credits

- [starlink-grpc-tools](https://github.com/sparky8512/starlink-grpc-tools) by sparky8512
