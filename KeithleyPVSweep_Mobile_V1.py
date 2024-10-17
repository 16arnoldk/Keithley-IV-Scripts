# -*- coding: utf-8 -*-
"""
Modified Script for Dual Keithley 2400 Voltage Sweep with Independent Compliance
"""

import pyvisa as visa
import time
import numpy as np
import matplotlib.pyplot as plt
import os


def initialize_Keithley(resource_name, compliance_current):
    # Getting resource manager
    rm = visa.ResourceManager()
    
    # Printing resources list and instrument ID
    print("----------RESOURCES-------------")
    print(rm.list_resources())
    print('\n')
   
    k2400 = rm.open_resource(resource_name)
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
    k2400.write(f':SENS:CURR:PROT {compliance_current}')
    k2400.write(':SENS:CURR:RANG:AUTO ON')
    
    # Set the measurement function to current only
    k2400.write(':SENS:FUNC "CURR"')
    
    return k2400


def Keithley_VOLTAGE_SWEEP(params):
    # Unpacking parameters
    Vmin, Vmax, step_size, compliance_current, Volt_Supp_Instr, Curr_Read_Instr, read_bias, compliance_read = params
    
    # Number of points to iterate through and record voltage data
    points = int((Vmax - Vmin) / step_size) + 1
    
    # Creating data holders
    t_values = []
    voltage_values = []
    current_values = []
    power_values = []
    voltage_1_values = []
    current_1_values = []
    power_1_values = []
    power_2_values = []
    
    # Enabling output for both Keithleys
    Volt_Supp_Instr.write(':OUTP ON')
    Curr_Read_Instr.write(':OUTP ON')
    
    # Setting the static bias for Keithley 2
    Curr_Read_Instr.write(f':SOUR:VOLT {read_bias}')
    Curr_Read_Instr.write(f':SENS:CURR:PROT {compliance_read}')  # Set the compliance current for Keithley 2
    
    # Iterating over the voltage range
    start_time = time.time()
    for i in range(points):
        voltage = Vmin + i * step_size
        Volt_Supp_Instr.write(f':SOUR:VOLT {voltage}')
        
        # Giving delay for measurement to stabilize
        time.sleep(0.05)
        
        # Recording time
        t = time.time() - start_time
        
        # Querying the current from Keithley 1 (Volt_Supp_Instr)
        current = Volt_Supp_Instr.query_ascii_values(':READ?')[1]
        power = voltage * current
        
        # Querying the voltage and current from Keithley 2 (Curr_Read_Instr)
        voltage_1 = Curr_Read_Instr.query_ascii_values(':READ?')[0]
        current_1 = Curr_Read_Instr.query_ascii_values(':READ?')[1]
        power_1 = voltage_1 * current_1
        power_2 = voltage * current_1
        
        # Storing the values
        t_values.append(t)
        voltage_values.append(voltage)
        current_values.append(current)
        power_values.append(power)
        voltage_1_values.append(voltage_1)
        current_1_values.append(current_1)
        power_1_values.append(power_1)
        power_2_values.append(power_2)
        
        # Printing voltage and current at specific whole number voltages
        if int(voltage) == voltage:
            print(f'Voltage: {voltage:.2f} V, Current: {current_1:.6e} A')
    
    # Set source voltage to 0V after the sweep for both Keithleys
    Volt_Supp_Instr.write(':SOUR:VOLT 0')
    Curr_Read_Instr.write(':SOUR:VOLT 0')
    
    # Disabling output for both Keithleys
    Volt_Supp_Instr.write(':OUTP OFF')
    Curr_Read_Instr.write(':OUTP OFF')
    
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
        f.write('#! Type = pv-sweep\n')
        f.write('\n')
        
        # Writing the header
        f.write(f't\t\tV\t\tI\t\tP\t\tV1\t\tI1\t\tP1\t\tP2\n')
        
        # Writing the data
        for i in range(points):
            f.write(f'{t_values[i]:.6f}\t{voltage_values[i]:.2f}\t{current_values[i]:.6e}\t{power_values[i]:.6e}\t'
                    f'{voltage_1_values[i]:.2f}\t{current_1_values[i]:.6e}\t{power_1_values[i]:.6e}\t{power_2_values[i]:.6e}\n')
    
    print("Data saved successfully.")
    
    # Plotting the voltage of Keithley 1 vs. current of Keithley 2
    plt.figure(figsize=(8, 6))
    plt.plot(voltage_values, [abs(i) for i in current_1_values], label=f'V-I Curve ({Volt_Supp_Instr.resource_name} vs. {Curr_Read_Instr.resource_name})')
    plt.xlabel(f'Voltage (V) ({Volt_Supp_Instr.resource_name})')
    plt.ylabel(f'Current (A) ({Curr_Read_Instr.resource_name})')
    #plt.yscale('log')
    #plt.ylim(1E-10, 1E-1)
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
Vmin = 0        # Minimum voltage
Vmax = 12      # Maximum voltage
step_size = .1 # Voltage step size
compliance_current = 0.35  # Compliance current in Amperes for Keithley 1
read_bias = 0    # Static voltage for Keithley 2
compliance_read = 0.1  # Compliance current in Amperes for Keithley 2

# Initialize the Keithley 2400 instruments
Volt_Supp_Instr = initialize_Keithley('GPIB0::16::INSTR', compliance_current)
Curr_Read_Instr = initialize_Keithley('GPIB0::14::INSTR', compliance_read)

# Consolidating sweep parameters
sweep_params = [Vmin, Vmax, step_size, compliance_current, Volt_Supp_Instr, Curr_Read_Instr, read_bias, compliance_read]

# Perform the voltage sweep
Keithley_VOLTAGE_SWEEP(sweep_params)

# Cleanup Keithley
Volt_Supp_Instr.close()
Curr_Read_Instr.close()

exit()
