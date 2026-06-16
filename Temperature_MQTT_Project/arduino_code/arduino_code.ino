#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <DHT.h> // Include the DHT sensor library

// Initialize the LCD. 
// I2C Address is usually 0x27 or 0x3F. 16 columns, 2 rows.
LiquidCrystal_I2C lcd(0x27, 16, 2);

// --- Configuration ---
#define DHTPIN A0      // Signal pin connected to A0
#define DHTTYPE DHT11  // DHT 11 sensor type
DHT dht(DHTPIN, DHTTYPE);

String candidateName = "Uwase Teta Paola (user276)"; // Set to >16 chars to demonstrate scrolling
int nameLength;

// --- Timing and Scrolling Variables ---
int scrollPos = 0;
unsigned long lastScrollTime = 0;
const int scrollDelay = 400; // Milliseconds between scroll shifts

unsigned long lastTempReadTime = 0;
const int tempReadDelay = 2000; // Read temperature every 2 seconds

void setup() {
  // Trade Code: SPE
  // 1. Setup Serial Communication for sending data to PC
  Serial.begin(9600);
  
  // 2. Setup LCD
  lcd.init();
  lcd.backlight();
  nameLength = candidateName.length();

  // 3. Setup DHT Sensor
  dht.begin();
}

void loop() {
  unsigned long currentMillis = millis();

  // ---------------------------------------------------------
  // TASK C: Handle LCD Scrolling for Row 1
  // ---------------------------------------------------------
  if (currentMillis - lastScrollTime >= scrollDelay) {
    lastScrollTime = currentMillis;
    lcd.setCursor(0, 0);
    
    if (nameLength <= 16) {
      // If name is short enough, just print it normally
      lcd.print(candidateName);
      // Pad with spaces to clear any old characters
      for(int i = nameLength; i < 16; i++) lcd.print(" ");
    } else {
      // If name > 16 chars, scroll horizontally
      // We append the name to itself with some padding to create an infinite loop effect
      String displayString = candidateName + "   " + candidateName; 
      
      // Print exactly 16 characters starting from the current scroll position
      lcd.print(displayString.substring(scrollPos, scrollPos + 16));
      
      scrollPos++;
      // Once we have scrolled through the whole name + padding, reset to start
      if (scrollPos > nameLength + 3) {
        scrollPos = 0; 
      }
    }
  }

  // ---------------------------------------------------------
  // TASK B: Handle Temperature Reading & Serial Transmission
  // ---------------------------------------------------------
  if (currentMillis - lastTempReadTime >= tempReadDelay) {
    lastTempReadTime = currentMillis;
    
    // Read temperature as Celsius
    float temperatureC = dht.readTemperature();
    
    // Check if any reads failed and exit early (to try again).
    if (isnan(temperatureC)) {
      Serial.println("Failed to read from DHT sensor!");
      return;
    }
    
    // Display Temperature on LCD Row 2
    lcd.setCursor(0, 1);
    lcd.print("Temp: ");
    lcd.print(temperatureC, 1); // 1 decimal place
    lcd.print(" C     ");       // Trailing spaces to overwrite old text
    
    // Send the temperature via Serial to the PC client
    Serial.println(temperatureC);
  }
}
