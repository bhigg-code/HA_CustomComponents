# Atlona Matrix Integration for Home Assistant

Custom component for controlling Atlona OPUS matrix switchers via Home Assistant.

## Supported Devices
- AT-OPUS-810M (8x10 HDBaseT Matrix)
- Other Atlona matrices with telnet control (may require adjustments)

## Features
- **Media Player entities** for each output zone
- **Select entities** for inline source selection dropdowns
- **Switch entities** for master power and per-zone power control
- Real-time status updates via telnet polling

## Installation

1. Copy the `atlona_matrix` folder to your Home Assistant `custom_components` directory
2. Restart Home Assistant
3. Go to Settings → Devices & Services → Add Integration
4. Search for "Atlona Matrix" and configure with your device IP

## Configuration
- **Host**: IP address of your Atlona matrix
- **Port**: Telnet port (default: 23)

## Entities Created

For each configured zone:
- `media_player.atlona_<zone_name>` - Media player with source selection
- `select.atlona_<zone_name>_input` - Dropdown for source selection  
- `switch.atlona_<zone_name>_power` - Zone power on/off

Global:
- `switch.atlona_master_power` - Master power control

## Customization

Edit `media_player.py` to customize:
- `INPUT_NAMES` - Map input numbers to friendly names
- `OUTPUT_NAMES` - Map output numbers to zone names
