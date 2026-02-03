# JVC Projector Integration for Home Assistant

Custom component for controlling JVC projectors (NZ series and others) via network.

## Supported Devices
- JVC NZ900, NZ800, NZ700
- Other JVC projectors with network control (port 20554)

## Features
- **Power control** - Turn projector on/off
- **Input selection** - Switch between HDMI 1 and HDMI 2
- **Picture mode** - Change picture modes (Film, Cinema, Natural, HDR10, etc.)
- **Sensors** - Model, laser hours, firmware version, power status

## Installation

1. Copy the `jvc_projector` folder to your Home Assistant `custom_components` directory
2. Restart Home Assistant
3. Go to Settings → Devices & Services → Add Integration
4. Search for "JVC Projector" and configure

## Configuration
- **IP Address**: IP of your JVC projector
- **Port**: Network control port (default: 20554)
- **Password**: Network password if enabled on projector

## Entities Created

- `remote.jvc_projector` - Power on/off control
- `select.jvc_projector_input` - Input source selection
- `select.jvc_projector_picture_mode` - Picture mode selection
- `sensor.jvc_projector_model` - Model name
- `sensor.jvc_projector_laser_hours` - Laser/lamp hours
- `sensor.jvc_projector_firmware` - Firmware version
- `sensor.jvc_projector_power_status` - Power state (on/off/warming/cooling)

## Troubleshooting

If connection fails with "PJNAK":
1. Check if network password is enabled on projector
2. Enter the password in the integration configuration
3. Or disable password: Menu → Network → Password → Off
