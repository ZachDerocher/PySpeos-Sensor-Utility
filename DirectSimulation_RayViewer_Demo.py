from pathlib import Path
import os
import numpy as np

from sensor_utils import lxp_viewer_util
from sensor_utils import measures_export_util

from ansys.speos.core import Project, Speos, launcher, sensor
from ansys.speos.core import Body, Face, Part



HOSTNAME = "localhost"
GRPC_PORT = 50098  # Be sure the Speos GRPC Server has been started on this port.
USE_DOCKER = False  # Set to False if you're running this example locally as a Notebook.

if USE_DOCKER:
    speos = Speos(host=HOSTNAME, port=GRPC_PORT)
else:
    speos = launcher.launch_local_speos_rpc_server(port=GRPC_PORT, version="252")

if USE_DOCKER:  # Running on the remote server.
    assets_data_path = Path("/app") / "assets"
else:
    assets_data_path = Path("C:\\Users\\zderoche\\DocumentsLocal\\git\\pyspeos\\tests\\assets\\")
    model_data_path =  os.getcwd() + "\\Reflector\\SimExport\\ProjectorSim20_2025R2.speos\\ProjectorSim20_2025R2.speos"

p = Project(
    speos=speos,
    path=str(model_data_path),
)

# run the LXP viewer for interactive simulation
#interactive_sim = lxp_viewer_util.create_interactive_sim(p)
#lxp_viewer_util.view_interactive_lxp(speos, p, interactive_sim)

# this demonstrates how to add an Intensity Sensor
# === Create Sensor ===
origin = [0, 0, 0]
direction = [0, 1, 0, 0, 0, 1, 1, 0, 0]

SENSOR_NAME = "Intensity_New"
sensor1 = p.create_sensor(name=SENSOR_NAME, feature_type=sensor.SensorXMPIntensity)

sensor1.set_type_spectral()

sensor_x_size = [-70, 70]
sensor_y_size = [-15, 15]
sensor_x_sampling = 1000
sensor_y_sampling = int(sensor_x_sampling * abs(sensor_y_size[1] - sensor_y_size[0]) / abs(sensor_x_size[1] - sensor_x_size[0]))

sensor1.x_start = sensor_x_size[0]
sensor1.x_end = sensor_x_size[1]
sensor1.x_sampling = sensor_x_sampling
sensor1.y_start = sensor_y_size[0]
sensor1.y_end = sensor_y_size[1]
sensor1.y_sampling = sensor_y_sampling

sensor1.set_layer_type_none()
sensor1.set_axis_system([*origin, *direction])
sensor1.commit()

# run the direct simulation, with LXP enabled
sim_name ="ProjectorSim"
sim = p.find(sim_name)[0]
sim.set_stop_condition_rays_number(int(1e4))
sensors_list = sim.get('sensor_paths')
sensors_list.append(SENSOR_NAME)
sim.set_sensor_paths(sensors_list)
sim.set_light_expert(True)
sim.commit()
sim_result = sim.compute_CPU()


# export the measures from the intensity sensor
#intensity_sensor = p.find(name="", name_regex=True, feature_type=sensor.SensorXMPIntensity)[0]
#measures_result_png = measures_export_util.measures_export(sim, intensity_sensor, os.getcwd())

# run the LXP viewer for direct simulation, including ray filtering GUI
lxp_data = lxp_viewer_util.lxp_viewer_util(speos, p, sim, run_gui=True)
for sensor in range(0, len(lxp_data)):
    ray_data = lxp_data[sensor].rays
    print(ray_data[0])


#root_part = p.find(name="", feature_type=Part) # root part
#subpart = p.find(name="RootPart/", name_regex=True) # all bodies under root
#housing_body = subpart[11]
#p.preview()
