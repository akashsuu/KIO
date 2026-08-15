#pragma once

// Wi-Fi Configuration
const char* WIFI_SSID = "YOUR_WIFI_SSID";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";

// PC Server Configuration
// Change this to the IP address printed when you run the Python server
const char* SERVER_IP = "192.168.1.100";
const int SERVER_PORT = 5000;

// NTP Time Configuration
const long UTC_OFFSET_SECONDS = 0; // Adjust to your timezone (e.g., 3600 for +1h)

// Animation timing
const int FRAME_DELAY_MS = 100;
