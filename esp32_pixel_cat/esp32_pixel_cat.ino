#include <Arduino.h>
#include <Adafruit_GFX.h>
#include <Adafruit_ST7735.h>
#include <SPI.h>
#include <PNGdec.h>
#include "config.h"
#include "frames.h"

// Forward declaration to prevent Arduino IDE compile errors
int pngDraw(PNGDRAW *pDraw);

Adafruit_ST7735 tft = Adafruit_ST7735(TFT_CS, TFT_DC, TFT_RST);
PNG png;

int currentFrameIndex = 0;
unsigned long lastFrameTime = 0;
bool testPassed = false;

// Draw callback for PNGdec
int pngDraw(PNGDRAW *pDraw) {
    uint16_t lineBuffer[160];
    png.getLineAsRGB565(pDraw, lineBuffer, PNG_RGB565_BIG_ENDIAN, 0xffffffff);
    tft.drawRGBBitmap(0, pDraw->y, lineBuffer, pDraw->iWidth, 1);
    return 0;
}

void playNextFrame() {
    if (NUM_SIT_FRAMES == 0) return;
    
    int rc = png.openFLASH((uint8_t*)sit_frames[currentFrameIndex], sit_frame_sizes[currentFrameIndex], pngDraw);
    if (rc == PNG_SUCCESS) {
        Serial.printf("Frame %d: %dx%d\n", currentFrameIndex, png.getWidth(), png.getHeight());
        png.decode(NULL, 0);
        png.close();
    } else {
        Serial.printf("Failed to decode frame %d, error: %d\n", currentFrameIndex, rc);
    }
    
    currentFrameIndex++;
    if (currentFrameIndex >= NUM_SIT_FRAMES) {
        currentFrameIndex = 0;
    }
}

void setup() {
    Serial.begin(115200);
    delay(1000);
    Serial.println("=== Pixel Cat Booting ===");
    
    // Try GREENTAB2 - most common for 1.8" 128x160 TFT modules
    tft.initR(INITR_GREENTAB);
    tft.setRotation(0); // Portrait mode: 128 wide x 160 tall
    
    // === DIAGNOSTIC TEST ===
    // Draw colored blocks so you can confirm the display is working
    tft.fillScreen(ST77XX_RED);
    delay(500);
    tft.fillScreen(ST77XX_GREEN);
    delay(500);
    tft.fillScreen(ST77XX_BLUE);
    delay(500);
    tft.fillScreen(ST77XX_BLACK);
    
    tft.setTextColor(ST77XX_WHITE);
    tft.setTextSize(1);
    tft.setCursor(10, 10);
    tft.println("Pixel Cat!");
    tft.setCursor(10, 30);
    tft.printf("Frames: %d", NUM_SIT_FRAMES);
    tft.setCursor(10, 50);
    tft.printf("Size: %d bytes", sit_frame_sizes[0]);
    
    Serial.printf("Total frames: %d\n", NUM_SIT_FRAMES);
    Serial.printf("Frame 0 size: %d bytes\n", sit_frame_sizes[0]);
    
    delay(2000);
    tft.fillScreen(ST77XX_BLACK);
    
    testPassed = true;
    Serial.println("=== Starting Animation ===");
}

void loop() {
    if (testPassed && millis() - lastFrameTime > FRAME_DELAY_MS) {
        playNextFrame();
        lastFrameTime = millis();
    }
}
