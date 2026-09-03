"""Constants for the BLE Gastank integration."""

DOMAIN = "ble_gastank"

CONF_SENSOR_TYPE = "sensor_type"
SENSOR_TYPE_DIMES = "dimes"
SENSOR_TYPE_TRUMA = "truma"

SENSOR_TYPES = {
    SENSOR_TYPE_DIMES: "DIMES BLE Sensor",
    SENSOR_TYPE_TRUMA: "Truma LevelControl",
}

# Manufacturer ID für DIMES (ggf. anpassen)
COMPANY_ID_DIMES = 0xFFFF

# Truma BLE UUIDs
TRUMA_SERVICE_UUID = "22bfa701-6afe-4cc5-b3ff-3e140baedeb6"
TRUMA_MEASUREMENT_DATA_UUID = "22bfa710-6afe-4cc5-b3ff-3e140baedeb6"
