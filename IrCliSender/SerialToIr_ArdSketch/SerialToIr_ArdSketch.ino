// IR Sender Sketch for Command Prompt Control
// Connect IR LED to Pin 3 (with a transistor or suitable driver circuit)

#include <Arduino.h>
#include <IRremote.hpp>

// Define the IR send pin as requested (Digital Pin 3)
#define IR_SEND_PIN 3 

// Buffer for storing received RAW timing data
#define MAX_RAW_LEN 85 // Max length of your recorded RAW codes (around 84-85 entries)
uint16_t rawTimings[MAX_RAW_LEN];

void setup() {
    Serial.begin(115200);
    // Initialize IR sender (Carrier frequency is 38 kHz by default)
    IrSender.begin(IR_SEND_PIN, ENABLE_LED_FEEDBACK);
    
    Serial.println(F("IR Sender Ready. Send raw timing data via serial (Format: RAW:<len>:<t1>,<t2>,...)."));
}

void loop() {
    if (Serial.available()) {
        String input = Serial.readStringUntil('\n');
        input.trim();

        // Expected format from Python: RAW:<len>:<t1>,<t2>,...
        if (input.startsWith("RAW:")) {
            
            // 1. Extract length and timings string
            int firstColon = input.indexOf(':');
            int secondColon = input.indexOf(':', firstColon + 1);
            
            if (firstColon == -1 || secondColon == -1) {
                Serial.println(F("ERROR: Invalid format."));
                return;
            }

            // Length is between the first and second colon
            String lenStr = input.substring(firstColon + 1, secondColon);
            uint16_t len = (uint16_t)lenStr.toInt();

            // Timings are after the second colon
            String timingsStr = input.substring(secondColon + 1);

            // 2. Check length validity
            if (len == 0 || len > MAX_RAW_LEN) {
                Serial.print(F("ERROR: Invalid length ("));
                Serial.print(len);
                Serial.println(F(")."));
                return;
            }
            
            // 3. Parse timings into the array
            int currentIndex = 0;
            int lastComma = -1;

            for (uint16_t i = 0; i < len; i++) {
                int nextComma = timingsStr.indexOf(',', lastComma + 1);
                String timingStr;

                if (nextComma == -1) {
                    // Last element
                    timingStr = timingsStr.substring(lastComma + 1);
                } else {
                    timingStr = timingsStr.substring(lastComma + 1, nextComma);
                }
                
                rawTimings[currentIndex++] = (uint16_t)timingStr.toInt();

                if (nextComma == -1) {
                    break;
                }
                lastComma = nextComma;
            }

            // 4. Send the IR signal
            // Panasonic remotes typically use 38 kHz
            IrSender.sendRaw(rawTimings, len, 38);

            Serial.print(F("SENT: "));
            Serial.print(len);
            Serial.println(F(" raw marks/spaces."));
            
        } else {
            Serial.println(F("ERROR: Unknown command."));
        }
    }
}