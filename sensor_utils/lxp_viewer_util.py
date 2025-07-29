import os
import numpy as np
import matplotlib.pyplot as plt

from ansys.speos.core import LightPathFinder, sensor, source
from ansys.speos.core.simulation import SimulationInteractive
import ansys.speos.core.workflow.open_result as orf

from sensor_utils import lxp_filter_tool as lxp_filter_tool
from importlib import reload
reload(lxp_filter_tool)

def get_sensor_objects(p):
    """
    retrieves all sensors from a sim
    (note: only finds irradiance, radiance, and intensity sensors)
    """
    sensor_irradiance_objects = p.find(name="", name_regex=True, feature_type=sensor.SensorIrradiance)
    sensor_types = len(sensor_irradiance_objects)*['irradiance']
    sensor_radiance_objects = p.find(name="", name_regex=True, feature_type=sensor.SensorRadiance)
    sensor_types = sensor_types + len(sensor_radiance_objects)*['radiance']
    sensor_intensity_objects = p.find(name="", name_regex=True, feature_type=sensor.SensorXMPIntensity)
    sensor_types = sensor_types + len(sensor_intensity_objects)*['intensity']

    sensor_objects = sensor_irradiance_objects + sensor_radiance_objects + sensor_intensity_objects
    
    return sensor_objects, sensor_types

def get_result_names(sim, sensor_objects):
    """
    retrieves names of sensors and results
    """
    sim_name = sim.get("name")
    sensor_names = []
    results_names = []
    for i in range(0, len(sensor_objects)):
        #results_names.append(sensor_objects[i].get("result_file_name"))
        this_name = sensor_objects[i].get("name").split(':')
        sensor_names.append(this_name[0])
        results_names.append(sim_name + '.' + this_name[0])
    return results_names, sensor_names
    
def get_intensity_map(dpf_instance, png_path):

    # get the array size
    n_x = dpf_instance.XNb
    n_y = dpf_instance.YNb
    # get the array size
    w_x = dpf_instance.XSampleWidth
    w_y = dpf_instance.YSampleHeight

    xmp_data = np.zeros([n_y, n_x])
    for row in range(0, n_y):
        y = dpf_instance.YMin + w_y*(row + 0.5) # half pix shift to center coords
        for col in range(0, dpf_instance.XNb):
            x = dpf_instance.XMin + w_x*(col + 0.5) # half pix shift to center coords
            xmp_data[row, col] = dpf_instance.GetValue1(x, y) # units are lx for irradiance map
    # normalize the data
    xmp_data = 255 * xmp_data * np.max(xmp_data)
    xmp_data = np.flip(xmp_data)
    plt.imsave(png_path, xmp_data, cmap='jet')  


def export_result_to_png(sim, sensor_name, results_name, sensor_type):
    """
    exports a stored xmp result to png
    """
    xmp_path = orf._find_correct_result(sim, results_name + ".xmp")
    if xmp_path == '':
        for res in sim.result_list:
            if ('.xmp' in res.path) & (sensor_name in res.path):
                xmp_path = res.path
                break
    #orf.open_result_image(simulation_feature=sim, result_name=xmp_path) # single-liner pyspeos tool, but it opens a pop-up window...
    png_path = xmp_path[0:len(xmp_path)-3] + 'png'

    if os.name == "nt":
        from comtypes.client import CreateObject
    try:
        dpf_instance = CreateObject("XMPViewer.Application")
    except:
        import subprocess
        viewer_path = r"C:\Program Files\ANSYS Inc\v251\Optical Products\Viewers\Xmpviewer.exe"
        dpf_instance = subprocess.Popen([viewer_path, xmp_path])

    dpf_instance.OpenFile(xmp_path)
    if sensor_type=='intensity':
        #get_intensity_map(dpf_instance, png_path)
        dpf_instance.SetColorMode(10) # iso level color
        res = dpf_instance.ExportXMPImage(png_path, 1)
        
    elif sensor_type=='radiance':
        dpf_instance.SetColorMode(6) # true color
        res = dpf_instance.ExportXMPImage(png_path, 1)
    else:
        dpf_instance.SetColorMode(0) # false color
        res = dpf_instance.ExportXMPImage(png_path, 1)

    # Close XMPViewer
    pid=dpf_instance.GetPID
    cmd = 'taskkill /PID ' + str(pid) + ' /F'
    os.system(cmd)

    return png_path
    

def lxp_viewer_util(speos, p, sim):
    """
    utility function to start up the lxp viewer GUI
    """
    
    # get the sensor 3d coordinates and orientation
    sensor_objects, sensor_types = get_sensor_objects(p)

    # get the result as a png file
    result_name, sensor_names = get_result_names(sim, sensor_objects)

    png_paths = []
    lxp_data = []
    for i in range(0, len(result_name)):
        # create a png of the xmp result (for viewing in GUI)
        this_png_path = export_result_to_png(sim, sensor_names[i], result_name[i], sensor_types[i])
        png_paths.append(this_png_path)

        # retrieve the lxp data
        lpf_path = this_png_path[0:-3] + "lpf"
        print(lpf_path)
        lxp = LightPathFinder(speos, lpf_path) # this process is very slow for a complex model
        lxp_data.append(lxp)

    # run the lxp gui
    lxp_filter_tool.run_lxp_viewer(png_paths, p, lxp_data, sensor_objects, sensor_names, sensor_types)


def create_interactive_sim(p):
    # get the list of sensor objects
    sensor_objects = p.find(name="", name_regex=True, feature_type=sensor.SensorIrradiance)
    sensor_names = []
    for i in range(0, len(sensor_objects)):
        sensor_names.append(sensor_objects[i].get("name"))
    print(sensor_names)

    # get the list of source objects
    # (all geometry already included by default)

    source_objects = p.find(name="", name_regex=True, feature_type=source.SourceSurface)
    source_names = []
    for i in range(0, len(source_objects)):
        source_names.append(source_objects[i].get("name"))
    #print(source_names)


    interactive_sim = p.create_simulation("InteractiveSim_LXP_Test", feature_type=SimulationInteractive)
    interactive_sim.set_source_paths(source_names)
    interactive_sim.set_sensor_paths(sensor_names)
    interactive_sim.set_light_expert(True)

    interactive_sim.commit()
    return interactive_sim


def view_interactive_lxp(speos, p, interactive_sim):
    
    import ansys.speos.core.workflow.open_result as orf
    results = interactive_sim.compute_CPU()
    path = orf._find_correct_result(interactive_sim, "InteractiveSim_LXP_Test.lpf", download_if_distant=False)
    lxp = LightPathFinder(speos, path)
    lxp.preview(project=p)