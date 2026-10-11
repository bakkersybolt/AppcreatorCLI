---
trigger: glob
globs: "{src,include,lib}/**/*.{cpp,h,hpp}, platformio.ini"
description: "Strikte standaarden voor ESP32 PlatformIO C++ firmware ontwikkeling."
---

# ESP32 C++ & PlatformIO Regels

## Geheugenbeheer & Stabiliteit

- Vermijd onnodige dynamische geheugenallocaties (`malloc`, `new`, grote dynamische `String` operaties in loops). Gebruik `char[]` of vaste buffers waar mogelijk om heap fragmentation te voorkomen.
- Controleer periodiek `ESP.getFreeHeap()` bij geheugen-intensieve taken zoals JSON parsing of WiFi communicatie.
- Gebruik voor JSON altijd **ArduinoJson v7** met `JsonDocument`.

## Non-Blocking Architecture

- Gebruik NOOIT lange `delay()` aanroepen in de `loop()`. Gebruik `millis()` timers of FreeRTOS tasks (`vTaskDelay()`).
- Zorg dat de watchdog timer nooit getriggerd wordt door blokkerende lussen.

## Serial & Logging

- Gebruik standaard baudrate **115200**.
- Gebruik gestructureerde log output of JSON payloads voor seriële telemetrie.
