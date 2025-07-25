from pathlib import Path
import os

from sensor_utils import lxp_viewer_util
from sensor_utils import measures_export_util

from ansys.speos.core import Project, Speos, launcher, sensor
from ansys.speos.core import Body, Face, Part


HOSTNAME = "localhost"
GRPC_PORT = 50098  # Be sure the Speos GRPC Server has been started on this port.
speos = launcher.launch_local_speos_rpc_server(port=GRPC_PORT, version="252")

model_data_path =  os.getcwd() + "\\Reflector\\SimExport\\ProjectorSim20_2025R2.speos\\ProjectorSim20_2025R2.speos"

p = Project(
    speos=speos,
    path=str(model_data_path),
)

# run the LXP viewer for interactive simulation
#interactive_sim = lxp_viewer_util.create_interactive_sim(p)
#lxp_viewer_util.view_interactive_lxp(speos, p, interactive_sim)

# run the direct simulation, with LXP enabled
sim_name ="ProjectorSim"
sim = p.find(sim_name)[0]
sim.set_stop_condition_rays_number(int(1e4))
sim.set_light_expert(True)
sim.commit()
sim_result = sim.compute_CPU()

# run the LXP viewer for direct simulation, including ray filtering GUI
lxp_viewer_util.lxp_viewer_util(speos, p, sim)

# under construction...
# export the measures from the intensity sensor
#intensity_sensor = p.find(name="", name_regex=True, feature_type=sensor.SensorXMPIntensity)[0]
#measures_export_util.measures_export(sim, intensity_sensor)

#root_part = p.find(name="", feature_type=Part) # root part
#subpart = p.find(name="RootPart/", name_regex=True) # all bodies under root
#housing_body = subpart[11]
#p.preview()
