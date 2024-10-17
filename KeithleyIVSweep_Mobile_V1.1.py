# -*- coding: utf-8 -*-
"""
Modified Script for Keithley 2400 Voltage Sweep
"""

import pyvisa as visa
import time
import numpy as np
import matplotlib.pyplot as plt
import os


def initialize_Keithley():
    # Getting resource manager
    rm = visa.ResourceManager()
    
    # Printing resources list and instrument ID
    print("----------RESOURCES-------------")
    print(rm.list_resources())
    print('\n')
   
    k2400 = rm.open_resource('GPIB0::12::INSTR')
    k2400.read_termination = '\n'
    k2400.write_termination = '\n'
    
    print("----------INSTRUMENT-------------")
    print(k2400.query('*IDN?'))
    print('\n')
    
    # Restoring GPIB defaults and setting status to preset
    k2400.write("*rst; status:preset;")
    
    # Set the source function to voltage
    k2400.write(':SOUR:FUNC VOLT')
    
    # Set the voltage to 0 initially
    k2400.write(':SOUR:VOLT 0')
    
    # Set the compliance current limit and enable auto-ranging
    k2400.write(':SENS:CURR:PROT 150E-3')
    k2400.write(':SENS:CURR:RANG:AUTO ON')
    
    # Set the measurement function to current only
    k2400.write(':SENS:FUNC "CURR"')
    
    return k2400


def Keithley_VOLTAGE_SWEEP(params):
    # Unpacking parameters
    Vmin, Vmax, step_size, compliance_current, Keithley = params
    
    # Number of points to iterate through and record voltage data
    points = int((Vmax - Vmin) / step_size) + 1
    
    # Creating data holders
    t_values = []
    voltage_values = []
    current_values = []
    power_values = []
    
    # Enabling output
    Keithley.write(':OUTP ON')
    
    # Iterating over the voltage range
    start_time = time.time()
    for i in range(points):
        voltage = Vmin + i * step_size
        Keithley.write(f':SOUR:VOLT {voltage}')
        
        # Giving delay for measurement to stabilize
        time.sleep(0.05)
        
        # Recording time, querying the current measurement, and calculating power
        t = time.time() - start_time
        current = Keithley.query_ascii_values(':READ?')[1]
        power = voltage * current
        
        # Storing the time, voltage, current, and power
        t_values.append(t)
        voltage_values.append(voltage)
        current_values.append(current)
        power_values.append(power)
        
        # Printing voltage and current at specific whole number voltages
        if int(voltage) == voltage:
            print(f'Voltage: {voltage:.2f} V, Current: {current:.6e} A')
    
    # Set source voltage to 0V after the sweep
    Keithley.write(':SOUR:VOLT 0')
    
    # Disabling output
    Keithley.write(':OUTP OFF')
    
    # Path for saved files
    directory = r'C:\semspace\Saved GC Data'
    
    # Get filename from user
    filename = input("Enter filename: ")
    filename = filename + ".txt"
    
    # Writing the data to a .txt file
    with open(os.path.join(directory, filename), 'w') as f:
        # Writing the preamble
        f.write('*! Laptop Compatible "Mobile" Version of QKeithleyControlMaster\n')
        f.write('*! Project = Fill project details here\n')
        f.write('#! Fluence / Dose / Condition = Fill measurement details here\n')
        f.write('#! Type = iv-sweep\n')
        f.write('\n')
        
        # Writing the header
        f.write(f't\t\tV\t\tI\t\tP\n')
        
        # Writing the data
        for i in range(points):
            f.write(f'{t_values[i]:.6f}\t{voltage_values[i]:.2f}\t{current_values[i]:.6e}\t{power_values[i]:.6e}\n')
    
    print("Data saved successfully.")
    
    # Plotting the data with a logarithmic scale for current
    plt.figure(figsize=(8, 6))
    plt.plot(voltage_values, [abs(i) for i in current_values], label='I-V Curve')
    plt.xlabel('Voltage (V)')
    plt.ylabel('Current (A)')
    plt.yscale('log')
    plt.ylim(1E-10, 1E-1)
    plt.title('Voltage Sweep (Log Scale)')
    plt.legend()
    plt.grid(True, which="both", ls="--")
    plt.show()


#--------------------------------------------------------   
#-------------------------------------------------------- 
# Beginning of Program
#--------------------------------------------------------
#--------------------------------------------------------  
    
# Parameters for the voltage sweep
Vmin = -2        # Minimum voltage
Vmax = 2        # Maximum voltage
step_size = 0.1  # Voltage step size
compliance_current = 0.10  # Compliance current in Amperes

# Initialize the Keithley 2400
Keithley = initialize_Keithley()

# Consolidating sweep parameters
sweep_params = [Vmin, Vmax, step_size, compliance_current, Keithley]

# Perform the voltage sweep
Keithley_VOLTAGE_SWEEP(sweep_params)

# Cleanup Keithley
Keithley.close()

exit()
