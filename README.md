# Grundfos ALPHA2 GO for Home Assistant

Custom Home Assistant integration for Grundfos ALPHA2 GO circulation pumps over Bluetooth LE.

> Early development project. Current support is limited to BLE connectivity, device information and diagnostic notifications. Flow, head, power and RPM decoding are planned.

## Current features

- Bluetooth LE connection to ALPHA2 GO pumps
- Multiple pumps via separate config entries
- Device name, model and firmware sensors
- Connection status sensor
- Notification activity counter

## Roadmap

- [x] Basic BLE connection
- [x] Device information sensors
- [x] Fix config flow import issue
- [ ] Automatic Bluetooth discovery
- [ ] BLE diagnostic capture
- [ ] JSONL export for reverse engineering
- [ ] Decode flow, head, power and RPM

## Installation during development

Copy `custom_components/grundfos_alpha2go` into your Home Assistant `/config/custom_components/` directory, then restart Home Assistant.

## Notes

The Grundfos proprietary BLE service has been identified, but the application payload still needs reverse engineering before real pump metrics can be exposed.