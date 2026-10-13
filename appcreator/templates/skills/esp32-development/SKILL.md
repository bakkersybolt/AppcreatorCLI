---
name: esp32-development
description: "Praktische ontwikkelgids voor ESP32 microcontrollers met PlatformIO, WiFi/MQTT telemetrie en FreeRTOS."
---

# Skill: esp32-development

**Doel:** Assisteren bij embedded firmware ontwikkeling voor de ESP32 met behulp van PlatformIO.

## PlatformIO CLI Commando's

Voer deze commando's uit in de root van het project:

```bash
# Firmware compileren
pio run

# Flashen naar de aangesloten ESP32
pio run --target upload

# Seriële monitor openen (baudrate 115200)
pio device monitor -b 115200

# Compileren, flashen en direct monitor starten
pio run --target upload && pio device monitor -b 115200
```

## WiFi Verbinding Patroon

```cpp
#include <WiFi.h>

const char* ssid = "JOUW_WIFI_SSID";
const char* password = "JOUW_WIFI_WACHTWOORD";

void setupWiFi() {
    Serial.printf("Verbinden met %s...", ssid);
    WiFi.begin(ssid, password);
    
    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 20) {
        delay(500);
        Serial.print(".");
        attempts++;
    }
    
    if (WiFi.status() == WL_CONNECTED) {
        Serial.println("\n✅ WiFi Verbonden!");
        Serial.printf("IP-adres: %s\n", WiFi.localIP().toString().c_str());
    } else {
        Serial.println("\n❌ WiFi Verbinding Mislukt!");
    }
}
```
