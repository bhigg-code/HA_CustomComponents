"""Sensor entities for JVC Projector."""
import logging

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up JVC Projector sensor entities."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        JvcModelSensor(coordinator, entry),
        JvcLaserHoursSensor(coordinator, entry),
        JvcSoftwareVersionSensor(coordinator, entry),
        JvcPowerStatusSensor(coordinator, entry),
    ])


class JvcModelSensor(CoordinatorEntity, SensorEntity):
    """Sensor for JVC Projector model."""

    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"jvc_projector_model_{entry.entry_id}"
        self._attr_name = "JVC Projector Model"
        self._attr_icon = "mdi:projector"

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
        )

    @property
    def native_value(self) -> str | None:
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get("model")


class JvcLaserHoursSensor(CoordinatorEntity, SensorEntity):
    """Sensor for JVC Projector laser hours."""

    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"jvc_projector_laser_hours_{entry.entry_id}"
        self._attr_name = "JVC Projector Laser Hours"
        self._attr_icon = "mdi:timer-outline"
        self._attr_native_unit_of_measurement = "h"
        self._attr_device_class = SensorDeviceClass.DURATION

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
        )

    @property
    def native_value(self) -> int | None:
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get("laser_hours")


class JvcSoftwareVersionSensor(CoordinatorEntity, SensorEntity):
    """Sensor for JVC Projector software version."""

    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"jvc_projector_software_version_{entry.entry_id}"
        self._attr_name = "JVC Projector Firmware"
        self._attr_icon = "mdi:chip"

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
        )

    @property
    def native_value(self) -> str | None:
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get("software_version")


class JvcPowerStatusSensor(CoordinatorEntity, SensorEntity):
    """Sensor for JVC Projector power status."""

    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"jvc_projector_power_status_{entry.entry_id}"
        self._attr_name = "JVC Projector Power Status"
        self._attr_icon = "mdi:power"

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
        )

    @property
    def native_value(self) -> str | None:
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get("power")
