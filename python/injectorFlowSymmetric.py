#---SYMMETRIC INJECTOR FLOW CALCULATOR---
# version 1.2.1

from dearpygui.core import *
from dearpygui.simple import *
import math
import numpy as np
import pandas as pd

#set initial window configuration (purely cosmetic)
set_main_window_size(1000, 650)
set_main_window_title("Symmetric Injector Flow Calculator | MRS")
set_theme("Dark")

calc_run_number = 0

#variables to save values of last run
#saving in another variable in case user makes changes to the input fields before clicking Export
last_dx = None
last_theta = None
last_v = None
last_a = None

def importFile():
    try:
        import_filepath = get_value("filepath_field")
        
        if not import_filepath[-4:] == ".txt":
            import_filepath = import_filepath + ".txt"
            
        log_info("Importing inputs from " + import_filepath, logger="Logs")
        import_file = open(import_filepath, "r")
    except:
        log_error("Import failed. Check filepath.", logger="Logs")
        return

    try:
        import_lines = import_file.readlines()
        if not import_lines[0][18:-1] == "1.2.1":
            log_warning("Save file version does not match software version. Import might fail.", logger="Logs")
        set_value(name="dx_field", value=import_lines[4][23:-1])
        set_value(name="theta_field", value=import_lines[5][13:-1])
        set_value(name="velocity_field", value=import_lines[6][26:-1])
        set_value(name="accel_field", value=import_lines[7][22:-1])

    except:
        log_error("Import failed. Check file formatting.", logger="Logs")
        return
    
    log_info("Import successful.", logger="Logs")
    computeFlow()

def exportFile():
    if not calc_run_number > 0:
        log_error("Cannot export. Run the calculations first.", logger="Logs")
        return

    exportFilename = get_value("filepath_field")
    
    if not exportFilename == "" or exportFilename == None:
        log_info("Attempting export...", logger = "Logs")
        if not (len(exportFilename) > 4 and exportFilename[-4:] == ".txt"):
            exportFile = exportFilename + ".txt"
    else:
        log_error("Please enter file name for export.", logger = "Logs")

    try:
        result_file = open(exportFile, "w")
        result_file.write("Save file version 1.2.1\n\n")
        result_file.write("INPUTS\n\n")
        result_file.write("Dx (horizontal dist.): ")
        result_file.write(str(last_dx)+"\n")
        result_file.write("Theta (deg): ")
        result_file.write(str(last_theta)+"\n")
        result_file.write("Injector Exit Vel. (m/s): ")
        result_file.write(str(last_v)+"\n")
        result_file.write("Acceleration (m/s^2): ")
        result_file.write(str(last_a)+"\n")
        result_file.write("\nOUTPUTS\n\n")
        result_file.write("Flow intersect time (s): ")
        result_file.write(str(get_value("tx"))+"\n")
        result_file.write("Flow intersect Dy (m): ")
        result_file.write(str(get_value("dy"))+"\n")
        result_file.write("Jet collision angle (deg): ")
        result_file.write(str(get_value("fi"))+"\n")
        log_info("Inputs saved in " + exportFile, logger = "Logs")
    except:
        log_error("TXT export failed.", logger = "Logs")  

def computeFlow():
    global calc_run_number
    calc_run_number += 1
    log_info(message = "Run [" + str(calc_run_number) + "]: Computing flow...", logger = "Logs")

    x_vals = []
    y_vals = []

    try:
        dx = float(get_value("dx_field"))
        theta = math.radians(float(get_value("theta_field")))
        v = float(get_value("velocity_field"))
        a = float(get_value("accel_field"))
    except:
        log_error("Input error. Make sure all design parameters are float values.", logger = "Logs")

    global last_dx, last_theta, last_v, last_a
    last_dx = dx
    last_theta = math.degrees(theta)
    last_v = v
    last_a = a

    log_info("Inputs:\n" +
             "Horiz. Dist.: " + str(dx) + " m\n"
             "Theta: " + str(math.degrees(theta)) + " deg\n"
             "Inj. Exit Vel.: " + str(v) + "m/s\n"
             "Accel.: " + str(a) + "m/s^2", logger = "Logs")

    tx = dx/(v*math.sin(theta))
    dy = (tx*(a*tx + 2*v*math.cos(theta)))/2

    set_value(name = "dy", value = dy)
    set_value(name = "tx", value = abs(tx))

    delta_t = tx/100
    delta_x = dx*(delta_t/tx)
    delta_y = (delta_t*(a*delta_t + 2*v*math.cos(theta)))/2

    for c in range(0, 100):
        x_vals.append(delta_x)
        y_vals.append(delta_y)
        delta_t = delta_t + tx/100
        delta_x = dx*(delta_t/tx)
        delta_y = (delta_t*(a*delta_t + 2*v*math.cos(theta)))/2

    add_line_series(name="Flow Curve" , plot="flow_curve",x=x_vals, y=y_vals)
    collision_angle = min(2*(90-math.degrees(math.atan((y_vals[-1]-y_vals[-2])/(x_vals[-1]-x_vals[-2])))), (360-2*(90-math.degrees(math.atan((y_vals[-1]-y_vals[-2])/(x_vals[-1]-x_vals[-2]))))))
    set_value(name="fi", value = collision_angle)
    
    if get_value("mirror_check"):
        x_vals_m = []
        for x in x_vals:
            x_vals_m.append(-x+2*dx)
        add_line_series(name="Flow Curve (M)" , plot="flow_curve",x=x_vals_m, y=y_vals)
    else:
        delete_series(plot="flow_curve",series="Flow Curve (M)")

    log_info("Done.", logger = "Logs")

#FILE OPERATIONS BAR
with window("File I/O", width=960, height=60, no_close=True, no_move=True):
    set_window_pos("File I/O", 10, 10)
    add_input_text(name="filepath_field", label="Filepath", tip = "If the file is in the same directory with the script, you don't need\nto write the full path.")
    add_same_line()
    add_button("Import", callback = importFile)
    add_same_line()
    add_button("Export", callback = exportFile)
        
#INPUTS WINDOW
with window("Input", width=450, height=220):   
    set_window_pos("Input", 10, 80)
    add_text("Enter design parameters in float values.")
    add_spacing(count=6)
    add_input_text(name = "dx_field", label = "Horiz. Dist. (m)", tip="Dist. to the centerline between two injectors.")
    add_input_text(name = "theta_field", label = "Theta (deg)", tip="Angle from vertical axis.\nEnter positive val. for above horizon, negative for below.")
    add_input_text(name = "velocity_field", label = "Flow Exit Vel. (m/s)")
    add_input_text(name = "accel_field", label = "Accel. (m/s^2)", tip="Acceleration FELT BY THE FLOW, not the vessel. Positive axis is up.")
    add_spacing(count=6)
    add_button("Compute Flow", callback = computeFlow)
    add_same_line()
    add_checkbox(name="mirror_check", label="Mirror Graph", tip="This only affects graph visualization. Exported data always uses single curve.")

#OUTPUTS WINDOW
with window("Output", width=500, height=510):
    set_window_pos("Output", 470, 80)
    add_input_text(name="dy_output", label="Vert. Dist. (m)", source="dy", readonly=True, enabled=False)
    add_input_text(name="tx_output", label="Intersect Time (s)", source="tx", readonly=True, enabled=False)
    add_input_text(name="ca_output", label="Collision Angle (deg)", source="fi", readonly=True, enabled=False)
    add_plot(name="flow_curve", label="Flow",
             x_axis_name="X Axis (m)", y_axis_name = "Y Axis (m)", equal_aspects = True)

#LOG WINDOW
with window("Log", width=450, height=280):
    set_window_pos("Log", 10, 310)
    add_logger("Logs", log_level=0, autosize_x = True, autosize_y = True)

start_dearpygui()
