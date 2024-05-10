import pyvisa
import time
import numpy as np
import os
# path to folder to save text file measurement data
path_to_folder = 'd:/Python/Ametek_DSP_7270_signal_recovery/impedance_spectroscopy_voltage_A_channel/text_file/16_Bipolar_slow_scan_amp_1V/'
# path to text file to save data
root_name_file = 'ametek_dsp_7270_impedance_spect'
# path to file with TC / time constants
path_to_TC_file='d:/Python/Ametek_DSP_7270_signal_recovery/impedance_spectroscopy_voltage_A_channel/TC_command_table_noisemode_off/TC_command_table_noisemode_off.txt'
# load time constant data to numpy array
TC_data=np.loadtxt(path_to_TC_file, dtype=float, delimiter='\t')
# time constant adat shape
TC_data_shape=TC_data.shape
# number of time constants
no_TC_data_values=TC_data_shape[0]
# start pyVISA Resource manager
rm = pyvisa.ResourceManager()
print(rm)
# acquire and print possible connections
rm.list_resources()
print(rm.list_resources())
# open TCPIP SOCKET connection to the Ametek DSP 7270 Signal Recovery lock-in
ametek_inst = rm.open_resource('TCPIP0::147.213.112.60::50000::SOCKET')
# termination characters for reading and writing
ametek_inst.read_termination = '\r\n'
ametek_inst.write_termination = '\r\n'
# set reference input
# set reference to internal input = 0
# set reference to external rear panel input = 1
# set reference to external front panel input = 2
# set refernec input to internal clock
ametek_inst.write('IE 0')
time.sleep(1)
# select current / voltage mode input selector
# current mode off, voltage mode input disabled
# connect signal to A
# current mode off - voltage mode input enabled
# high bandwidth current mode enabled = 1
# low noise current mode enabled  = 2
ametek_inst.write('IMODE 0')
time.sleep(1)
# volatge input configuration
# 0 both inputs grounded (tets mode)
# 1 A input only
# 2 -B input only
# 3 A-B differential mode
ametek_inst.write('VMODE 1')
time.sleep(1)
# FET input selection
# 0 Bipolar
# 1 FET
ametek_inst.write('FET 1')
time.sleep(1)
# full scale sensitivity control
ametek_inst.write('SEN 27')
time.sleep(1)
# set DC coupling
# 0 AC coupled
# 1 DC coupled
ametek_inst.write('DCCOUPLE 0')
### set AC gain control to automatic mode = 1
##ametek_inst.write('AUTOMATIC 1')
# set AC gain control to manual mode = 0
ametek_inst.write('AUTOMATIC 0')
time.sleep(1)
# set AC gain to 0 dB
ametek_inst.write('ACGAIN 0')
time.sleep(1)
# input connector shield float / ground control
# equal to 0 (ground)
# equal to 1 (conncted to ground via 1 kOhm resistor)
ametek_inst.write('FLOAT 0')
time.sleep(1)
# turn off line frequency rejection filter
# enable 50 or 60 Hz notch filter
# remove 50 Hz frequency
#ametek_inst.write('LF 1 1')
ametek_inst.write('LF 0 0')
time.sleep(1)
# set time constant to 1 seconds
ametek_inst.write('TC 15')
time.sleep(1)
### set auto phase (auto quadrature null)
### the instrument adjust the refernec phase to maximize X and minimize Y
##ametek_inst.write('AQN')
##time.sleep(1)
# set oscillator amplitude control to 0.1 V
ametek_inst.write('OA. 1.0E0')
time.sleep(1)
# logarithmic frequency
# logarithmic exponent - start
log_exp_start=5.0
# logarithmic exponent - stop
log_exp_stop=0.0
# logarithmic exponent - step
log_exp_step=-0.1
# number of logarithmic steps
no_log_steps=int((log_exp_stop-log_exp_start)/log_exp_step)+1
# wait additional time for settting lock-in parameters
time.sleep(5)
# initialize folder counter
counter_folder=0
# number of counter folder digits
counter_folder_digits=6
# number of total readings per single frequency
total_readings=100
# main loop
for index_0 in range(no_log_steps):
    # calculate current logarithmic exponent
    log_exp_current=log_exp_start+index_0*log_exp_step
    # convert counter folder to string
    counter_folder_str=str(counter_folder)
    counter_folder_str=counter_folder_str.rjust(counter_folder_digits, '0')
    # create path to subfolder
    path_to_subfolder=path_to_folder + counter_folder_str
    # create subfolder
    os.mkdir(path_to_subfolder)
    # specify path to measurement file
    path_to_file=path_to_subfolder + '/' + root_name_file + '_' + counter_folder_str + '.txt'
    # iterate counter folder
    counter_folder=counter_folder+1
    # calculate actual / current frequency
    current_freq=pow(10,log_exp_current)
    print(current_freq)
    # set oscillation frequency control in Hz
    # oscillation frequency control command in floating mode
    osc_freq_cmd='OF.'
    # oscillation frequency value converted to scientific notation
    osc_freq_value="{:.6e}".format(current_freq)
    # oscillation frquency control string
    osc_freq_string=osc_freq_cmd + ' ' + osc_freq_value
    # set oscillation frequency
    ametek_inst.write(osc_freq_string)
    time.sleep(5)
    # calculate period in seconds
    period=float(1/current_freq)
    print(period)
    # calculate waiting time in measurement collection
    wait_time=period
    for index_1 in range(no_TC_data_values):
        if (TC_data[index_1][1] <= period):
            # update your time constant index
            index_TC=index_1+1
    # find appropriate time constant selection number
    TC_constant_selector=str(int(TC_data[index_TC][0]))
    # set time constant to appropriate value in seconds
    TC_command='TC '+TC_constant_selector
    ametek_inst.write(TC_command)
    time.sleep(1)
    print(TC_command)
    # create buffer to store measurement data as numpy array
    buffer = np.array([], dtype=float)
    # create buffer for actual measurement
    single_meas = np.zeros([1,6], dtype=float)
    # create counter to count measurement
    counter = 1
    # switch off noise mode  = 0
    # switch on noise mode = 1
    ametek_inst.write('NOISEMODE 0')
    time.sleep(1)
    # perform an autosensitivity operation
    ametek_inst.write('AS')
    time.sleep(5)
    # second loop
    for index_2 in range(total_readings):
        # reads Magnitude value in Volts
        ametek_inst.write('MAG.')
        data_mag = ametek_inst.read_raw()
        #print(data_mag)
        #print(list(data_mag))
        data_mag_len=len(data_mag)
        for index_3 in range(data_mag_len):
            if (data_mag[index_3] == 0):
                last_zero=index_3
                #print(last_zero)
        data_mag_seleced_bytes=data_mag[(last_zero+1):(data_mag_len-1)]
        try:
            mag_value=float(data_mag_seleced_bytes.decode('utf-8'))
        except:
            mag_value=9.99999999999E+06
        #print(mag_value)
        #time.sleep(wait_time/5)
        time.sleep(0.01)
        # reads Phase value in degrees
        ametek_inst.write('PHA.')
        data_pha = ametek_inst.read_raw()
        #print(data_pha)
        #print(list(data_pha))
        data_pha_len=len(data_pha)
        for index_3 in range(data_pha_len):
            if (data_pha[index_3] == 0):
                last_zero=index_3
                #print(last_zero)
        data_pha_seleced_bytes=data_pha[(last_zero+1):(data_pha_len-1)]
        try:
            pha_value=float(data_pha_seleced_bytes.decode('utf-8'))
        except:
            pha_value=9.99999999999E+06
        #print(pha_value)
        #time.sleep(wait_time/5)
        time.sleep(0.01)
        # reads X value in Volts
        ametek_inst.write('X.')
        data_x = ametek_inst.read_raw()
        #print(data_x)
        #print(list(data_x))
        data_x_len=len(data_x)
        for index_3 in range(data_x_len):
            if (data_x[index_3] == 0):
                last_zero=index_3
                #print(last_zero)
        data_x_seleced_bytes=data_x[(last_zero+1):(data_x_len-1)]
        try:
            x_value=float(data_x_seleced_bytes.decode('utf-8'))
        except:
            x_value=9.99999999999E+06
        #print(x_value)
        #time.sleep(wait_time/5)
        time.sleep(0.01)
        # reads Y value in Volts
        ametek_inst.write('Y.')
        data_y = ametek_inst.read_raw()
        #print(data_y)
        #print(list(data_y))
        data_y_len=len(data_y)
        for index_3 in range(data_y_len):
            if (data_y[index_3] == 0):
                last_zero=index_3
                #print(last_zero)
        data_y_seleced_bytes=data_y[(last_zero+1):(data_y_len-1)]
        try:
            y_value=float(data_y_seleced_bytes.decode('utf-8'))
        except:
            y_value=9.99999999999E+06
        #print(y_value)
        #time.sleep(wait_time/5)
        time.sleep(0.01)
        # reads Frequency value in Volts
        ametek_inst.write('FRQ.')
        data_frq = ametek_inst.read_raw()
        #print(data_frq)
        #print(list(data_frq))
        data_frq_len=len(data_frq)
        for index_3 in range(data_frq_len):
            if (data_frq[index_3] == 0):
                last_zero=index_3
                #print(last_zero)
        data_frq_seleced_bytes=data_frq[(last_zero+1):(data_frq_len-1)]
        try:
            frq_value=float(data_frq_seleced_bytes.decode('utf-8'))
        except:
            frq_value=9.99999999999E+06
        #print(frq_value)
        #time.sleep(wait_time/5)
        time.sleep(0.01)
        # insert measured values to the single measurement buffer
        single_meas[0][0] = float(float(counter)*wait_time)
        single_meas[0][1] = float(mag_value)
        single_meas[0][2] = float(pha_value)
        single_meas[0][3] = float(x_value)
        single_meas[0][4] = float(y_value)
        single_meas[0][5] = float(frq_value)
        # print measured data
        print(single_meas)
        # append single measurement data to buffer
        buffer = np.append(buffer, single_meas)
        #print(buffer)
        # increase counter
        counter += 1
        # size of buffer numpy array
        buffer_size = np.size(buffer)
        # print buffer size
        #print(buffer_size)
        no_rows =  int(buffer_size/6)
        # reshape buffer numpy array
        buffer_reshaped = np.reshape(buffer, (no_rows, 6))
        # save reshaped buffer numpy array
        np.savetxt(path_to_file, buffer_reshaped, delimiter='\t')
        # wait aditional time after fast reading of data
        time.sleep(wait_time)
        

