# ESP32 C++ & PlatformIO

## Niet blokkeren

- Gebruik geen `delay()` van meer dan een paar milliseconden in `loop()`: tijdens een delay worden wifi, sensoren en de watchdog niet bediend. Gebruik timers op basis van `millis()` of FreeRTOS-taken met `vTaskDelay()`.
- Geef wachtlussen een maximale duur, zodat de watchdog niet afgaat.

## Geheugen

- Vermijd dynamische allocatie in lussen (`new`, `malloc`, het aaneenrijgen van `String`). Dat fragmenteert de heap en leidt na uren tot crashes. Gebruik vaste buffers of `char[]`.
- Gebruik ArduinoJson v7 met `JsonDocument`.
- Log `ESP.getFreeHeap()` bij geheugenintensief werk zoals JSON of wifi.

## Geheimen

- Zet wifi-wachtwoorden en API-sleutels niet in de broncode. Gebruik `include/secrets.h`, dat in `.gitignore` staat.

## Serieel

- De baudrate is 115200, gelijk aan `monitor_speed` in `platformio.ini`.
- Schrijf telemetrie als JSON op één regel, zodat een script die kan inlezen.
