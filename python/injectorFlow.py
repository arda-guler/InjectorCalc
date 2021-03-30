from dearpygui.core import *
from dearpygui.simple import *
import math
import numpy as np
import pandas as pd

#set initial window configuration (purely cosmetic)
set_main_window_size(1000, 650)
set_main_window_title("Injector Flow Calculator | MRS")
set_theme("Dark")

calc_run_number = 0

##def importFile():
##    try:
##        import_filepath = get_value("load_path_field")
##        
##        if not import_filepath[-4:] == ".txt":
##            if import_filepath[-5:] == ".xlsx":
##                log_warning("Exported .xlsx files don't contain input info. Trying " + import_filepath[:-5] + ".txt instead...", logger="Logs")
##                import_filepath = import_filepath[:-5] + ".txt"
##            else:
##                import_filepath = import_filepath + ".txt"
##            
##        log_info("Importing inputs from " + import_filepath, logger="Logs")
##        import_file = open(import_filepath, "r")
##    except:
##        log_error("Import failed. Check filepath.", logger="Logs")
##        return
##
##    try:
##        import_lines = import_file.readlines()
##        set_value(name="throat_radius_field", value=import_lines[2][15:-1])
##        set_value(name="exit_radius_field", value=import_lines[3][13:-1])
##        set_value(name="chamber_radius_field", value=import_lines[4][16:-1])
##        set_value(name="expansion_ratio_field", value=import_lines[5][17:-1])
##        set_value(name="delta_n_field", value=import_lines[6][24:-1])
##        set_value(name="theta_FC_field", value=import_lines[7][10:-1])
##    except:
##        log_error("Import failed. Check file formatting.", logger="Logs")
##        return
##    
##    log_info("Import successful.", logger="Logs")

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

        excelFilename = get_value("filename_field")
    except:
        log_error("Input error. Make sure all design parameters are float values and export filename doesn't include illegal characters.", logger = "Logs")

    log_info("Inputs:\n" +
             "Horiz. Dist.: " + str(dx) + " m\n"
             "Theta: " + str(math.degrees(theta)) + " deg\n"
             "Inj. Exit Vel.: " + str(v) + "m/s\n"
             "Accel.: " + str(a) + "m/s^2", logger = "Logs")

    tx = dx/(v*math.sin(theta))
    dy = (tx*(a*tx + 2*v*math.cos(theta)))/2

    set_value(name = "dy", value = dy)

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
    
    if get_value("mirror_check"):
        x_vals_m = []
        for x in x_vals:
            x_vals_m.append(-x+2*dx)
        add_line_series(name="Flow Curve (M)" , plot="flow_curve",x=x_vals_m, y=y_vals)
    else:
        delete_series(plot="flow_curve",series="Flow Curve (M)")

    log_info("Done.", logger = "Logs")
        
#INPUTS WINDOW
with window("Input", width=450, height=220):   
    set_window_pos("Input", 10, 10)
    add_text("Enter design parameters in float values.")
    add_spacing(count=6)
    add_input_text(name = "dx_field", label = "Horiz. Dist. (m)", tip="Dist. to the centerline between two injectors.")
    add_input_text(name = "theta_field", label = "Theta (deg)")
    add_input_text(name = "velocity_field", label = "Flow Exit Vel. (m/s)")
    add_input_text(name = "accel_field", label = "Accel. (m/s^2)")
    add_spacing(count=6)
    #add_input_text(name = "filename_field", label = "Export Filename", tip = "Leave blank to skip export. File extension is automatic.")
    #add_spacing(count=6)
    add_button("Compute Flow", callback = computeFlow)
    add_same_line()
    add_checkbox(name="mirror_check", label="Mirror Graph", tip="This only affects graph visualization. Exported data always uses single curve.")
    #add_spacing(count=6)
    #add_text("Alternatively, you can import a previously saved .txt file.")
    #add_spacing(count=6)
    #add_input_text(name = "load_path_field", label = "Import Filepath", tip = "If the file is in the same directory with the script, you don't need\nto write the full path.")
    #add_spacing(count=6)
    #add_button("Import File", callback = importFile)

#OUTPUTS WINDOW
with window("Output", width=500, height=580):
    set_window_pos("Output", 470, 10)
    add_input_text(name="dy_output", label="Vert. Dist. (m)", source="dy", readonly=True, enabled=False)
    add_plot(name="flow_curve", label="Flow",
             x_axis_name="X Axis (m)", y_axis_name = "Y Axis (m)", equal_aspects = True)

#LOG WINDOW
with window("Log", width=450, height=360):
    set_window_pos("Log", 10, 240)
    add_logger("Logs", log_level=0, autosize_x = True, autosize_y = True)

start_dearpygui()
