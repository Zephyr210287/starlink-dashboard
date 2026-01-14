# Starlink Dashboard

A real-time web dashboard for monitoring your Starlink dish statistics via the local gRPC API.

![Dashboard Screenshot](./screenshot.png)

## Features

- **Real-time metrics**: Latency, download/upload speeds, power consumption
- **Visual sparklines**: 60-second history graphs for key metrics
- **Connection status**: State, uptime, drop rate, SNR quality
- **Dish position**: Azimuth, elevation, GPS satellite count
- **Obstruction tracking**: Percentage obstructed with visual indicator
- **Alerts display**: Active dish alerts
- **Auto-refresh**: Updates every 5 seconds
- **Responsive design**: Works on desktop and mobile

## Requirements

- Python 3.8+
- A Starlink dish on your local network (default: 192.168.100.1)
- [starlink-grpc-tools](https://github.com/sparky8512/starlink-grpc-tools)

## Installation

### 1. Clone this repository

```bash
git clone https://github.com/Zephyr210287/starlink-dashboard.git
cd starlink-dashboard
```

### 2. Install starlink-grpc-tools

```bash
git clone https://github.com/sparky8512/starlink-grpc-tools.git ~/starlink-grpc-tools
```

### 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the dashboard

```bash
python server.py
```

The dashboard will be available at `http://localhost:8100`

## Configuration

### Port and Host

```bash
python server.py --port 8080 --host 0.0.0.0
```

### starlink-grpc-tools Location

The server looks for starlink-grpc-tools in these locations (in order):

1. `STARLINK_GRPC_TOOLS` environment variable
2. `~/starlink-grpc-tools`
3. `~/src/starlink-grpc-tools`
4. `/opt/starlink-grpc-tools`

To use a custom location:

```bash
export STARLINK_GRPC_TOOLS=/path/to/starlink-grpc-tools
python server.py
```

## Running as a Service (systemd)

Create `~/.config/systemd/user/starlink-dashboard.service`:

```ini
[Unit]
Description=Starlink Dashboard
After=network.target

[Service]
Type=simple
WorkingDirectory=/path/to/starlink-dashboard
ExecStart=/usr/bin/python /path/to/starlink-dashboard/server.py -p 8100
Restart=always
RestartSec=5

[Install]
WantedBy=default.target
```

Enable and start:

```bash
systemctl --user daemon-reload
systemctl --user enable starlink-dashboard
systemctl --user start starlink-dashboard
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Dashboard HTML |
| `/api/status` | GET | Current dish status, obstruction, alerts |
| `/api/history` | GET | Historical stats and sparkline data |
| `/api/location` | GET | Dish location (if enabled) |
| `/api/reboot` | POST | Reboot the dish |
| `/api/stow` | POST | Stow/unstow the dish |

## Firewall

If accessing from other devices, open the port:

```bash
# UFW
sudo ufw allow 8100/tcp

# firewalld
sudo firewall-cmd --add-port=8100/tcp --permanent
sudo firewall-cmd --reload
```

## Troubleshooting

### "starlink_grpc module not found"

Ensure starlink-grpc-tools is installed and the path is correct:

```bash
git clone https://github.com/sparky8512/starlink-grpc-tools.git ~/starlink-grpc-tools
pip install grpcio yagrc
```

### "Connection refused" or timeout

- Verify your Starlink dish is accessible at 192.168.100.1
- Check that you're on the Starlink network (not behind a different router)
- Try: `curl http://192.168.100.1` to verify connectivity

### Dashboard shows "Error"

Check the server logs for detailed error messages. Common issues:
- Dish is rebooting or in a transitional state
- Network connectivity issues to the dish

## License

MIT License - see [LICENSE](LICENSE)

## Credits

- [starlink-grpc-tools](https://github.com/sparky8512/starlink-grpc-tools) by sparky8512
- Starlink dish gRPC API by SpaceX
