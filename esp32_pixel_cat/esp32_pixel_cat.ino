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

// Draw callback for PNGdec
int pngDraw(PNGDRAW *pDraw) {
    uint16_t lineBuffer[160];
    png.getLineAsRGB565(pDraw, lineBuffer, PNG_RGB565_BIG_ENDIAN, 0xffffffff);
    tft.drawRGBBitmap(0, pDraw->y, lineBuffer, pDraw->iWidth, 1);
    return 0;
}

void playNextFrame() {
    if (NUM_SIT_FRAMES == 0) return;
    
    // Read the PNG directly from PROGMEM (Flash Memory)
    int rc = png.openFLASH((uint8_t*)sit_frames[currentFrameIndex], sit_frame_sizes[currentFrameIndex], pngDraw);
    if (rc == PNG_SUCCESS) {
        png.decode(NULL, 0);
        png.close();
    } else {
        Serial.println("Failed to decode PNG frame");
    }
    
    currentFrameIndex++;
    if (currentFrameIndex >= NUM_SIT_FRAMES) {
        currentFrameIndex = 0;
    }
}

void setup() {
    Serial.begin(115200);
    
    // Initialize TFT
    tft.initR(INITR_BLACKTAB); 
    tft.setRotation(1); 
    tft.fillScreen(ST77XX_BLACK);
    
    Serial.println("Starting hardcoded animation!");
}

void loop() {
    if (millis() - lastFrameTime > FRAME_DELAY_MS) {
        playNextFrame();
        lastFrameTime = millis();
    }
}
