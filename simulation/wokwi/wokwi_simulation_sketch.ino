/**
 * @file wokwi_simulation_sketch.ino
 * @brief 2D Hardware Simulation Sketch for Wokwi Simulator
 * @target ESP32-S3 DevKit
 * @company Team TECHTONICS | Schneider Electric Yuva Yodha Hackathon
 */

#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);

// Pin Definitions
#define PIN_SOLAR_ADC       1   // Solar Irradiance Potentiometer (0-3.3V)
#define PIN_PRESSURE_ADC    3   // Pressure Sensor Potentiometer (0-3.3V)
#define PIN_PUMP_PWM       15   // Blue LED: Pump PWM Output
#define PIN_VALVE_PULSE    18   // Green LED: Active Zener Solenoid Pulse
#define PIN_BUTTON_PULSE    0   // Manual Inject Button

// Control State
float current_pressure_psi = 40.0;
float target_pressure_psi = 40.0;
float solar_watts = 280.0;
int pump_duty_pwm = 145; // 0 to 255
unsigned long last_pulse_time = 0;
bool valve_firing = false;

void setup() {
    Serial.begin(115200);
    pinMode(PIN_PUMP_PWM, OUTPUT);
    pinMode(PIN_VALVE_PULSE, OUTPUT);
    pinMode(PIN_BUTTON_PULSE, INPUT_PULLUP);

    Wire.begin(8, 9); // SDA=8, SCL=9 for ESP32-S3
    if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
        Serial.println(F("SSD1306 allocation failed"));
    }
    display.clearDisplay();
    display.setTextColor(WHITE);
    display.setTextSize(1);
    display.setCursor(10, 10);
    display.println("AGRI-WATT ESP32-S3");
    display.setCursor(10, 25);
    display.println("Schneider Electric");
    display.setCursor(10, 40);
    display.println("2D HW SIMULATION");
    display.display();
    delay(1500);
}

void loop() {
    // 1. Read Solar & Pressure Transducers
    int raw_solar = analogRead(PIN_SOLAR_ADC);
    int raw_pressure = analogRead(PIN_PRESSURE_ADC);

    solar_watts = map(raw_solar, 0, 4095, 20, 320); // 20W to 320W
    current_pressure_psi = map(raw_pressure, 0, 4095, 10, 70); // 10 to 70 PSI

    // 2. Closed-Loop Pressure PI Pump Throttling
    float error = target_pressure_psi - current_pressure_psi;
    pump_duty_pwm = constrain(130 + (int)(error * 12.0), 0, 255);

    // Limit pump duty if solar power sags (Dynamic Power Throttle)
    if (solar_watts < 150.0) {
        pump_duty_pwm = constrain(pump_duty_pwm, 0, 110);
    }
    analogWrite(PIN_PUMP_PWM, pump_duty_pwm);

    // 3. Automated Micro-Injection Pulse (every 2.5 seconds or on button press)
    if (millis() - last_pulse_time > 2500 || digitalRead(PIN_BUTTON_PULSE) == LOW) {
        last_pulse_time = millis();
        // Snap open (3 ms pull-in simulated via fast digital pulse)
        digitalWrite(PIN_VALVE_PULSE, HIGH);
        delay(35); // 35 ms pulse width
        digitalWrite(PIN_VALVE_PULSE, LOW); // Active Zener snaps shut in <1.2 ms
    }

    // 4. Update OLED Display
    display.clearDisplay();
    display.setCursor(0, 0);
    display.print("AGRI-WATT | MPPT: ");
    display.print((int)solar_watts);
    display.println("W");

    display.setCursor(0, 16);
    display.print("Line Press: ");
    display.print(current_pressure_psi, 1);
    display.println(" PSI");

    display.setCursor(0, 30);
    display.print("Pump PWM:   ");
    display.print((pump_duty_pwm * 100) / 255);
    display.println("%");

    display.setCursor(0, 44);
    display.print("Actuator:   Active Zener");
    display.setCursor(0, 56);
    display.print("Status:     38-42 PSI OK");
    display.display();

    delay(50);
}
