// Panasonic HK9327K IR Signal Recording Sketch
// This sketch sets the receive pin to 2 and forces UNKNOWN or PULSE_DISTANCE 
// protocols to output raw timing data for external analysis.

#include <Arduino.h>
#include <IRremote.hpp>

// Define the IR receive pin as requested (Digital Pin 2)
#define IR_RECEIVE_PIN 2

// Buffer size for raw data storage. 700 is typically sufficient for complex remotes.
#define RAW_BUFFER_LENGTH 700 
// The array type must be uint8_t to match the library function's requirement.
uint8_t sRawDataArray[RAW_BUFFER_LENGTH]; 

void setup() {
    Serial.begin(115200);

    // Print start message
    Serial.println(F("START IR Receiver Sketch (Finalized)"));
    
    // Start the IR receiver
    // ENABLE_LED_FEEDBACK will blink the built-in LED on reception
    IrReceiver.begin(IR_RECEIVE_PIN, ENABLE_LED_FEEDBACK);
    Serial.print(F("Ready to receive at pin "));
    Serial.println(IR_RECEIVE_PIN);
}

void loop() {
    // Check if data has been received and decoded
    if (IrReceiver.decode()) {
        
        // 1. Check if the protocol is fully decoded (e.g., NEC, SONY)
        // We exclude UNKNOWN and PULSE_DISTANCE, forcing them to the RAW block.
        if (IrReceiver.decodedIRData.protocol != UNKNOWN && IrReceiver.decodedIRData.protocol != PULSE_DISTANCE) {
            
            // Output format for known protocols: PROTOCOL:<protocol_name>,ADDRESS:<address>,COMMAND:<command>,BITS:<bits>
            
            Serial.print(F("PROTOCOL:"));
            Serial.print(IrReceiver.getProtocolString());
            
            Serial.print(F(",ADDRESS:0x"));
            Serial.print(IrReceiver.decodedIRData.address, HEX);
            
            Serial.print(F(",COMMAND:0x"));
            Serial.print(IrReceiver.decodedIRData.command, HEX);
            
            Serial.print(F(",BITS:"));
            Serial.println(IrReceiver.decodedIRData.numberOfBits);
            
        } else {
            // 2. Protocol is UNKNOWN or PULSE_DISTANCE (Panasonic) -> Output RAW data
            
            // Output format: RAW_DATA:<raw_len>:<mark1>,<space1>,<mark2>,<space2>,...
            
            uint16_t rawLen = IrReceiver.decodedIRData.rawlen;
            
            // Check for buffer overflow
            if (rawLen > RAW_BUFFER_LENGTH) {
                Serial.println(F("RAW_DATA:OVERFLOW"));
            } else {
                
                // Copy internal RAW data (in microseconds) to our array
                // The library function compensates for timing and stores the *ticks* in the uint8_t array.
                IrReceiver.compensateAndStoreIRResultInArray(sRawDataArray);
                
                Serial.print(F("RAW_DATA:"));
                Serial.print(rawLen);
                Serial.print(F(":"));
                
                // Output the RAW data array
                for (uint16_t i = 0; i < rawLen; i++) {
                    // Convert stored ticks (in uint8_t array) back to approximate microseconds (us).
                    // The common resolution is 50us per tick.
                    uint16_t duration_us = (uint16_t)sRawDataArray[i] * 50; 
                    
                    Serial.print(duration_us);
                    
                    if (i < rawLen - 1) {
                        Serial.print(F(","));
                    }
                }
                Serial.println();
            }
        }

        // Resume receiver to wait for the next signal
        IrReceiver.resume(); 
    }
}