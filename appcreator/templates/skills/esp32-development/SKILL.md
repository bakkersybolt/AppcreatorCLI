---
name: esp32-development
description: "Werkwijze voor ESP32-firmware met PlatformIO: compileren, flashen en de seriële monitor, een niet-blokkerende wifi-verbinding en het buiten de broncode houden van wachtwoorden. Gebruik bij elk werk aan de firmware in src/ of aan platformio.ini."
---

# ESP32-development

## PlatformIO

Voer deze commando's uit in de projectroot:

```bash
# Compileren
pio run

# Flashen naar de aangesloten ESP32
pio run --target upload

# Seriële monitor (115200 baud)
pio device monitor -b 115200

# Flashen en direct meekijken
pio run --target upload && pio device monitor -b 115200
```

Compileer na elke wijziging met `pio run`. Flashen kan alleen als er een bord is aangesloten; vraag dat na voordat je het probeert. Voeg bibliotheken toe onder `lib_deps` in `platformio.ini`.

## Wachtwoorden buiten de broncode

Maak `include/secrets.h` aan. Dat bestand staat in `.gitignore`:

```cpp
#pragma once

#define WIFI_SSID "naam-van-het-netwerk"
#define WIFI_PASSWORD "wachtwoord"
```

Voeg een `include/secrets.h.example` met lege waarden toe, zodat een ander weet wat er moet staan.

## Wifi zonder te blokkeren

Wacht niet in een lus met `delay()` op de verbinding: dan staat de rest van de firmware stil. Start de verbinding en controleer de status vanuit `loop()`:

```cpp
#include <WiFi.h>
#include "secrets.h"

const unsigned long WIFI_RETRY_INTERVAL_MS = 10000;
unsigned long lastWifiAttempt = 0;
bool wifiWasConnected = false;

void startWiFi() {
    WiFi.mode(WIFI_STA);
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    lastWifiAttempt = millis();
}

void maintainWiFi() {
    bool connected = WiFi.status() == WL_CONNECTED;

    if (connected && !wifiWasConnected) {
        Serial.printf("WiFi verbonden, IP: %s\n", WiFi.localIP().toString().c_str());
    } else if (!connected && millis() - lastWifiAttempt >= WIFI_RETRY_INTERVAL_MS) {
        Serial.println("WiFi niet verbonden, nieuwe poging...");
        WiFi.disconnect();
        WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
        lastWifiAttempt = millis();
    }

    wifiWasConnected = connected;
}
```

Roep `startWiFi()` aan in `setup()` en `maintainWiFi()` in `loop()`. De firmware herstelt zo ook zelf na een verbroken verbinding.

## Periodiek werk

Gebruik hetzelfde patroon als de heartbeat in `src/main.cpp`: onthoud het tijdstip van de laatste uitvoering en vergelijk met `millis()`. Het verschil `millis() - vorige` blijft kloppen als `millis()` na ongeveer 49 dagen overloopt.

## Problemen opsporen

- **Herstart in een lus:** lees de reden in de seriële monitor. `Guru Meditation` wijst op een ongeldige pointer of een te kleine stack; een watchdog-reset op code die te lang blokkeert.
- **Crash na uren:** log `ESP.getFreeHeap()`. Een dalende waarde wijst op een geheugenlek of fragmentatie.
- **Upload mislukt:** controleer de kabel en de poort met `pio device list`. Sommige borden vereisen dat de BOOT-knop wordt ingedrukt tijdens het verbinden.
