# AGRI-WATT: Hardware Pinout & Circuit Netlist Specification
**Target Controller**: ESP32-S3-WROOM-1 (Xtensa® Dual-Core 32-bit LX7 @ 240 MHz)

---

## 1. ESP32-S3 Pin Mapping Table

| GPIO Pin | Function | Peripheral / Mode | Connected Hardware Component | Electrical Specification |
| :--- | :--- | :--- | :--- | :--- |
| **GPIO 1** | PV Voltage Sense ($V_{pv}$) | ADC1_CH0 (12-bit, DMA) | Precision Resistor Divider (47k / 3.3k) | $0 - 50\text{ V}$ input scaled to $0 - 3.1\text{ V}$ |
| **GPIO 2** | PV Current Sense ($I_{pv}$) | ADC1_CH1 (12-bit, DMA) | INA180A3 High-Side Current Shunt ($50\text{ m}\Omega$) | $0 - 15\text{ A}$ scaled to $0 - 3.0\text{ V}$ ($200\text{ mV/A}$) |
| **GPIO 3** | Manifold Pressure Sense | ADC1_CH2 (12-bit, DMA) | Piezoresistive Ceramic Pressure Transducer | $0 - 100\text{ PSI}$ ratiometric ($0.5 - 4.5\text{ V}$ via divider) |
| **GPIO 4** | Bus Voltage Sense ($V_{bus}$) | ADC1_CH3 (12-bit, DMA) | Resistor Divider (22k / 3.3k) | $0 - 25\text{ V}$ rail scaled to $0 - 3.2\text{ V}$ |
| **GPIO 15**| Pump Motor PWM | MCPWM_UNIT_0, TIMER_0 | TC4427 Gate Driver $\rightarrow$ IRLZ44N Power MOSFET | $25\text{ kHz}$ hardware PWM with soft-start ramp |
| **GPIO 16**| Synchronous Buck PWM High | MCPWM_UNIT_0, TIMER_1A| IR2104 Half-Bridge Gate Driver (High-Side) | $100\text{ kHz}$ complementary with $150\text{ ns}$ dead-time |
| **GPIO 17**| Synchronous Buck PWM Low | MCPWM_UNIT_0, TIMER_1B| IR2104 Half-Bridge Gate Driver (Low-Side) | $100\text{ kHz}$ complementary with $150\text{ ns}$ dead-time |
| **GPIO 18**| Pulse Solenoid Valve #1 | MCPWM_UNIT_1, TIMER_0 | Optocoupler PC817 $\rightarrow$ Logic MOSFET (IRLZ44N) | Peak-and-Hold: $3\text{ ms}$ pull-in, $30\%$ hold PWM |
| **GPIO 19**| Reverse Purge Valve | Standard GPIO Output | 2N7002 $\rightarrow$ Miniature Pilot Solenoid | $12\text{ V}$ flush control valve |
| **GPIO 20**| Modbus-RTU TX | UART_NUM_1 TX | MAX485 / SP3485 RS-485 Transceiver (DI) | $9600 / 19200\text{ baud}$, 8-N-1, Schneider EcoStruxure |
| **GPIO 21**| Modbus-RTU RX | UART_NUM_1 RX | MAX485 / SP3485 RS-485 Transceiver (RO) | $9600 / 19200\text{ baud}$, 8-N-1, Schneider EcoStruxure |
| **GPIO 22**| RS-485 Flow Control (DE/RE) | Standard GPIO Output | MAX485 / SP3485 (DE & /RE tied together) | HIGH = Transmit, LOW = Receive |
| **GPIO 38**| System Status LED (RGB) | WS2812B / Addressable | On-board Diagnostic RGB LED | Green = Nominal, Blue = Solar Throttle, Red = Fault |

---

## 2. Active Zener Solenoid Snubber Netlist

```
   +12V Rail (Battery / Regulated Bus)
      |
      +-----------------------------+
      |                             |
      | + [C_bulk] 2200 uF 25V      |
      |   (Low-ESR Decoupling)     [L_coil] 12V Solenoid Valve Coil (45 mH, 18 Ohm)
      |                             |
     GND                            +-----------------------------------+
                                    |                                   |
                                    |                                  [A] D1: SS34 Ultrafast Schottky (40V, 3A)
                                    |                                  [K]
                                    |                                   |
                                    |                                  [K] ZD1: 36V 5W Zener Diode (1N5365B)
                                    |                                  [A]
                                    |                                   |
                                    |                                  +12V Rail (Forces High-Voltage Clamp)
                                    |
                                   [D] Q1: IRLZ44N Logic-Level N-Channel MOSFET
                                   [G] ---[ R_gate 100 Ohm ]--- (From PC817 Optocoupler via GPIO 18)
                                   [S] --- [ R_pulldown 100k ] --- GND
                                    |
                                   GND
```

### Turn-Off Clamping Physics:
1. When MOSFET Q1 switches OFF, inductive back-EMF spikes positively at the drain node.
2. The back-EMF forward-biases Schottky diode D1 and enters reverse breakdown on Zener diode ZD1.
3. The drain voltage is clamped firmly at:
   $$V_{drain} = V_{rail} + V_Z + V_{diode} = 12\text{ V} + 36\text{ V} + 0.4\text{ V} = 48.4\text{ V}$$
4. Since $V_{drain} = 48.4\text{ V} < 55\text{ V}$ ($V_{DSS}$ rating of IRLZ44N), the MOSFET is completely protected from avalanche breakdown.
5. Inductive current decay rate across the coil:
   $$\frac{di}{dt} = -\frac{V_Z + V_{diode}}{L} = -\frac{36.4\text{ V}}{0.045\text{ H}} = -808.8\text{ A/s}$$
6. Total demagnetization time from $I_{hold} = 200\text{ mA}$:
   $$t_{decay} = \frac{0.200\text{ A}}{808.8\text{ A/s}} = \mathbf{0.247\text{ ms}} \quad (\text{Mechanical closure verified } < 1.2\text{ ms})$$
