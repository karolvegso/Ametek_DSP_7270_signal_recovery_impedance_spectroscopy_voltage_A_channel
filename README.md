# Ametek_DSP_7270_signal_recovery_impedance_spectroscopy_voltage_A_channel
Ametek DSP 7270 signal_recovery - voltage channel monitoring a s a function of frequency

This Python script opens a TCP-IP connection at a specific IP address and port 50000 with an Ametek DSP 7270 signal recovery lock-in amplifier. It sets the internal clock to generate periodic reference signals with an internal clock. It sets the voltage mode for monitoring voltage values on Channel A. It sets the AC gain mode to manual and sets it to 0 dB. Then, the input connector is grounded (channel A), and the line frequency rejection filter is turned off. The transistor is set to FET. The coupling mode is set to AC coupling. The amplitude of the reference sinus signal is set to 1 V (OA. command). The auto phase is not used. 

The frequency is generated on the base 10. The exponents of frequency on the base ten are generated. In the main for loop, first, the reference signal frequency is set (OF. command), and the program waits for 5 seconds. From frequency, the period of the reference signal is calculated in seconds. According to the period, this program finds the suitable TC time constant in <TC_command_table_noisemode_off.txt> file. The TC constant should be equal to or larger than the period. Once the TC constant is set, the noise mode is switched off, and auto sensitivity is switched on. After switching auto sensitivity, the program waits again for 5 seconds. 

Then, the program reads <total_readings=100> times in a for loop these signals: the magnitude, phase, X, Y, and frequency of the signal (MAG., PHA., X., Y., FRQ.). For reading values, it does not use the query command of pyVISA, but instead it, it uses ametek_inst.read_raw() comamnd. It reads some strange byte sequence. Then, my program decodes that byte sequence to the float number. Sometimes, this decoding crashes. Therefore, I am using the try / except approach in Python to avoid the crash of my program. 

The time constant TC command table is also attached to this repository. Be careful with auto sensitivity. In my application, scanning from a larger frequency (10^5) to a lower frequency (10^0 Hz = 1 Hz) was better because auto sensitivity increased step-by-step, but it depends on your electric circuit.

Enjoy AMETEk signal recovery.
