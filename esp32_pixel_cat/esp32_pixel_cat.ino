#include <Arduino.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <LittleFS.h>
#include <TFT_eSPI.h>
#include <PNGdec.h>
#include <ArduinoJson.h>
#include <NTPClient.h>
#include <WiFiUdp.h>
#include "config.h"

TFT_eSPI tft = TFT_eSPI();
PNG png;
WiFiUDP ntpUDP;
NTPClient timeClient(ntpUDP, "pool.ntp.org", UTC_OFFSET_SECONDS);

// Animation State
String currentState = "idle";
String nextState = "idle";
std::vector<String> currentFrames;
int currentFrameIndex = 0;
unsigned long lastFrameTime = 0;
unsigned long stateStartTime = 0;

// Function declarations
void ensureConnected();
bool downloadAnimation(String animName);
void playNextFrame();
void updateBehavior();
int pngDraw(PNGDRAW *pDraw);

void setup() {
    Serial.begin(115200);
    
    tft.begin();
    tft.setRotation(1); // Adjust rotation if needed (128x160 portrait/landscape)
    tft.fillScreen(TFT_BLACK);
    
    if (!LittleFS.begin(true)) {
        Serial.println("LittleFS Mount Failed");
        return;
    }

    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    tft.setTextColor(TFT_WHITE);
    tft.drawString("Connecting Wi-Fi...", 10, 10);
    
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("\nConnected!");
    tft.fillScreen(TFT_BLACK);
    
    timeClient.begin();
    timeClient.update();
    
    // Initial state
    stateStartTime = millis();
    if (!downloadAnimation(currentState)) {
        Serial.println("Failed to load initial animation!");
    }
}

void loop() {
    ensureConnected();
    timeClient.update();
    
    updateBehavior();
    
    if (millis() - lastFrameTime > FRAME_DELAY_MS) {
        playNextFrame();
        lastFrameTime = millis();
    }
}

void ensureConnected() {
    if (WiFi.status() != WL_CONNECTED) {
        WiFi.disconnect();
        WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
        while (WiFi.status() != WL_CONNECTED) {
            delay(500);
        }
    }
}

// Draw callback for PNGdec
int pngDraw(PNGDRAW *pDraw) {
    uint16_t lineBuffer[160];
    png.getLineAsRGB565(pDraw, lineBuffer, PNG_RGB565_BIG_ENDIAN, 0xffffffff);
    tft.pushImage(0, pDraw->y, pDraw->iWidth, 1, lineBuffer);
    return 0;
}

// Draw from a LittleFS file directly to TFT
bool drawFrame(String filename) {
    File f = LittleFS.open(filename, "r");
    if (!f) return false;
    
    size_t size = f.size();
    uint8_t* buffer = (uint8_t*)malloc(size);
    if (!buffer) {
        f.close();
        return false;
    }
    f.read(buffer, size);
    f.close();
    
    int rc = png.openRAM(buffer, size, pngDraw);
    if (rc == PNG_SUCCESS) {
        tft.startWrite();
        png.decode(NULL, 0);
        tft.endWrite();
        png.close();
    }
    free(buffer);
    return rc == PNG_SUCCESS;
}

void playNextFrame() {
    if (currentFrames.size() == 0) return;
    
    String filepath = "/" + currentState + "/" + currentFrames[currentFrameIndex];
    if (!drawFrame(filepath)) {
        Serial.println("Failed to draw frame: " + filepath);
    }
    
    currentFrameIndex++;
    if (currentFrameIndex >= currentFrames.size()) {
        currentFrameIndex = 0;
        // Animation loop finished, transition to next state if requested
        if (currentState != nextState) {
            currentState = nextState;
            stateStartTime = millis();
            downloadAnimation(currentState);
        }
    }
}

bool downloadAnimation(String animName) {
    String url = "http://" + String(SERVER_IP) + ":" + String(SERVER_PORT) + "/api/animation/" + animName;
    HTTPClient http;
    http.begin(url);
    int httpCode = http.GET();
    
    if (httpCode != 200) {
        http.end();
        return false;
    }
    
    String payload = http.getString();
    http.end();
    
    DynamicJsonDocument doc(1024);
    deserializeJson(doc, payload);
    
    if (doc["error"]) {
        return false;
    }
    
    JsonArray frames = doc["frames"].as<JsonArray>();
    currentFrames.clear();
    
    // Create directory if not exists
    String dirPath = "/" + animName;
    if (!LittleFS.exists(dirPath)) {
        LittleFS.mkdir(dirPath);
    }
    
    for (JsonVariant v : frames) {
        String frameName = v.as<String>();
        currentFrames.push_back(frameName);
        
        String filePath = dirPath + "/" + frameName;
        
        // Cache check
        if (LittleFS.exists(filePath)) {
            continue; // Already downloaded
        }
        
        // Download frame
        String frameUrl = "http://" + String(SERVER_IP) + ":" + String(SERVER_PORT) + "/api/animation/" + animName + "/" + frameName;
        http.begin(frameUrl);
        int frameCode = http.GET();
        if (frameCode == 200) {
            File f = LittleFS.open(filePath, "w");
            if (f) {
                http.writeToStream(&f);
                f.close();
                Serial.println("Downloaded: " + filePath);
            }
        }
        http.end();
    }
    
    currentFrameIndex = 0;
    return true;
}

void updateBehavior() {
    // Only decide to change states if we have been in current state for a while
    if (millis() - stateStartTime < 5000) return;
    
    // Don't interrupt a transition that hasn't started yet
    if (currentState != nextState) return;

    int hour = timeClient.getHours();
    
    // Sleep schedule
    if (hour >= 23 || hour < 7) {
        nextState = "sleep";
    } else {
        // Random daytime behavior
        if (random(100) < 10) { // 10% chance to change state per check
            int r = random(5);
            if (r == 0) nextState = "idle";
            else if (r == 1) nextState = "sit";
            else if (r == 2) nextState = "walk";
            else if (r == 3) nextState = "jump";
            else if (r == 4) nextState = "play";
        } else {
            // Keep current daytime state, or default to idle if waking up
            if (currentState == "sleep") {
                nextState = "idle";
            }
        }
    }
}
