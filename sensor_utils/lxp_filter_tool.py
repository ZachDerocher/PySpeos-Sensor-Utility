
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk  
import numpy as np

from tkinter import Tk

class LxpGui:
    def __init__(self, master, png_paths, p, lxp, sensor_objs, sensor_names, sensor_types):
        self.master = master
        master.title("LXP Viewer")

        # dimensions of the main window
        master.geometry("600x700")

        self.sensor_idx = 0
        # get data from sensor object
        x_start = sensor_objs[self.sensor_idx].get('x_start')
        x_end = sensor_objs[self.sensor_idx].get('x_end')
        y_start = sensor_objs[self.sensor_idx].get('y_start')
        y_end = sensor_objs[self.sensor_idx].get('y_end')

        self.sensor_label = tk.Label(master, text='LXP Sensor:')
        self.sensor_label.place(relx=0.5, rely=0.26, anchor=tk.CENTER)
        self.sensor = tk.StringVar()
        self.sensor_selection = tk.OptionMenu(master, self.sensor, *sensor_names)
        self.sensor_selection.place(relx=0.5, rely=0.3, anchor=tk.CENTER)
        self.sensor.set(sensor_names[0])

        face_filters = ['none', '477333318']
        self.facefilter_label = tk.Label(master, text='Face Filter:')
        self.facefilter_label.place(relx=0.25, rely=0.26, anchor=tk.CENTER)
        self.facefilter = tk.StringVar()
        self.facefilter_selection = tk.OptionMenu(master, self.facefilter, *face_filters)
        self.facefilter_selection.place(relx=0.25, rely=0.3, anchor=tk.CENTER)
        self.facefilter.set(face_filters[0])

        self.roix_label = tk.Label(master, text='Target Area (X):')
        self.roix_label.place(relx=0.25, rely=0.06, anchor=tk.CENTER)
        self.roix = tk.StringVar()
        self.roix_entry = tk.Entry(master, textvariable=self.roix)
        self.roix_entry.place(relx=0.25, rely=0.1, anchor=tk.CENTER)
        self.roix_entry.insert(0, "0.0")

        self.roiy_label = tk.Label(master, text='Target Area (Y):')
        self.roiy_label.place(relx=0.25, rely=0.16, anchor=tk.CENTER)
        self.roiy = tk.StringVar()
        self.roiy_entry = tk.Entry(master, textvariable=self.roiy)
        self.roiy_entry.place(relx=0.25, rely=0.2, anchor=tk.CENTER)
        self.roiy_entry.insert(0, "0.0")

        self.roiw_label = tk.Label(master, text='Target Area (W):')
        self.roiw_label.place(relx=0.5, rely=0.06, anchor=tk.CENTER)
        self.roiw = tk.StringVar()
        self.roiw_entry = tk.Entry(master, textvariable=self.roiw)
        self.roiw_entry.place(relx=0.5, rely=0.1, anchor=tk.CENTER)
        default_w = 0.4*(x_end - x_start)
        self.roiw_entry.insert(0, str(int(default_w)))
        
        self.roih_label = tk.Label(master, text='Target Area (H):')
        self.roih_label.place(relx=0.5, rely=0.16, anchor=tk.CENTER)
        self.roih = tk.StringVar()
        self.roih_entry = tk.Entry(master, textvariable=self.roih)
        self.roih_entry.place(relx=0.5, rely=0.2, anchor=tk.CENTER)
        default_h = 0.4*(y_end - y_start)
        self.roih_entry.insert(0, str(int(default_h)))

        self.numrays_label = tk.Label(master, text='Number of Rays:')
        self.numrays_label.place(relx=0.75, rely=0.06, anchor=tk.CENTER)
        self.numrays_entry = tk.Entry(master)
        self.numrays_entry.place(relx=0.75, rely=0.1, anchor=tk.CENTER)
        self.numrays_entry.insert(0, "100")

        self.raylength_label = tk.Label(master, text='Length of Rays:')
        self.raylength_label.place(relx=0.75, rely=0.16, anchor=tk.CENTER)
        self.raylength_entry = tk.Entry(master)
        self.raylength_entry.place(relx=0.75, rely=0.2, anchor=tk.CENTER)
        self.raylength_entry.insert(0, "200")

        self.generate_plot(sensor_objs, png_paths, sensor_names, sensor_types)

        self.button_rays_viewer = tk.Button(master, text="Show Rays", command= lambda: self.show_rays(p, lxp[self.sensor_idx], sensor_objs[self.sensor_idx], sensor_types))
        self.button_rays_viewer.place(relx=0.75, rely=0.3, anchor=tk.CENTER)
        
        # add the traces
        self.roix.trace_add("write", lambda *args: self.update_roi())
        self.roiy.trace_add("write", lambda *args: self.update_roi())
        self.roiw.trace_add("write", lambda *args: self.update_roi())
        self.roih.trace_add("write", lambda *args: self.update_roi())
        self.sensor.trace_add("write", lambda *args: self.generate_plot(sensor_objs, png_paths, sensor_names, sensor_types))

    def update_sensor(self, sensor_names):
        # which sensor was chosen?
        for i in range(0, len(sensor_names)):
            if self.sensor.get() == sensor_names[i]:
                self.sensor_idx = i


    def generate_plot(self, sensor_objs, png_paths, sensor_names, sensor_types):
        # make sure we are updating the right sensor (this updates self.sensor_idx)
        self.update_sensor(sensor_names)

        sensor_obj = sensor_objs[self.sensor_idx]
        png_path = png_paths[self.sensor_idx]
        # get data from sensor object
        x_start = sensor_obj.get('x_start')
        x_end = sensor_obj.get('x_end')
        y_start = sensor_obj.get('y_start')
        y_end = sensor_obj.get('y_end')
        #x_samp = sensor_obj.get('x_sampling')
        #y_samp = sensor_obj.get('y_sampling')
        #self.pix_size_x = (x_end - x_start) / x_samp
        #self.pix_size_y = (y_end - y_start) / y_samp

        # set up matplotlib figure that will show the detector data
        mplfig = Figure(figsize = (6,4), dpi = 100)
        self.plot1 = mplfig.add_subplot(111)
        # plotting the graph
        plot_extent = [x_start, x_end, y_start, y_end]
        #sim = ax.imshow(img, interpolation='none', extent=plot_extent)
        img = plt.imread(png_path)
        self.plot1.imshow(img, interpolation='none', extent=plot_extent)
        self.plot1.grid(color='w', which='both', linestyle='-', linewidth=0.4)
        #self.plot1.minorticks_on()
        self.plot1.set_title('XMP Result for ' + sensor_names[self.sensor_idx])
        self.plot1.set_xlabel('Sensor X Coordinate (mm)')
        self.plot1.set_ylabel('Sensor Y Coordinate (mm)')
        if sensor_types[self.sensor_idx] == 'intensity':
            self.plot1.set_xlabel('Sensor X Coordinate (deg)')
            self.plot1.set_ylabel('Sensor Y Coordinate (deg)')
        mplfig.tight_layout()
        # creating the Tkinter canvas containing the Matplotlib figure
        self.canvas = FigureCanvasTkAgg(mplfig, master = self.master)  
        self.canvas.draw()
        self.canvas.get_tk_widget().place(relx=0.5, rely=0.65, anchor=tk.CENTER)
        self.update_roi()

    def update_roi(self):
        try:
            x = float(self.roix.get())
            y = float(self.roiy.get())
            w = int(self.roiw.get())
            h = int(self.roih.get())
        except:
            return

        roi = plt.Rectangle([x-0.5*w, y-0.5*h], w, h, color='r',fill=False)
        try:
            self.patch.remove()
        except:
            pass
        self.patch = self.plot1.add_patch(roi)

        # placing the canvas on the Tkinter window
        self.canvas.draw()
        #self.canvas.get_tk_widget().pack()
        self.canvas.get_tk_widget().place(relx=0.5, rely=0.65, anchor=tk.CENTER)
    
    def show_rays(self, p, lxp, sensor_obj, sensor_types):
        # clear the filter rays
        while lxp.filtered_rays:
            lxp.filtered_rays.pop()
        # find rays which meet the condition
        num_rays = int(self.numrays_entry.get())
        lxp = self.filter_rays(lxp, sensor_obj, sensor_types, num_rays)
        # preview in pyvista window
        ray_length = int(self.raylength_entry.get())
        if lxp.filtered_rays==[]:
            # no filtered rays found; don't show any rays
            p.preview(viz_args={"opacity": 0.7})
            return
        lxp.preview(project=p, max_ray_length=ray_length, ray_filter=True)

    def filter_rays(self, filtered_lxp, sensor_obj, sensor_types, num_rays):
        # filter the rays based on the selected filter area
        rays = filtered_lxp.rays
        filter_idx = []
        x = float(self.roix.get())
        y = float(self.roiy.get())
        w = int(self.roiw.get())
        h = int(self.roih.get())

        # check the sensor type
        sensor_type = sensor_types[self.sensor_idx]

        # get the sensor geometry
        sensor_axis = sensor_obj.get("axis_system") # x, y, z, xx, xy, xz, yx, yy, yz, zx, zy, zz
        po = np.array(sensor_axis[0:3]) # sensor plane origin
        pn = np.array(sensor_axis[9:12]) # sensor plane normal vector
        #v = po + np.array(sensor_axis[3:6]) # any point on sensor plane
        M = np.array([sensor_axis[3:6], sensor_axis[6:9], sensor_axis[9:12]])
        
        if sensor_type == "intensity":
            # intensity sensor origin is at the sphere center point
            # normal vector is along the angular (0,0) axis.
            # for filtering, we will check ray position on a far-field plane centered on normal vector axis
            # scale sensor plane position, so it is far-field
            far_field_dist = 1e100
            po = po + far_field_dist * pn

        # check ray filter criteria
        for i in range(0, filtered_lxp.nb_traces):
            
            # face filter
            face_filter = self.facefilter.get()
            if face_filter == 'none':
                pass
            else:
                hit_bodies = rays[i].get('body_ids')
                hit_faces = rays[i].get('face_ids')
                if (int(face_filter) not in hit_faces) & (int(face_filter) not in hit_bodies):
                    continue
            
            # lxp viewing zone
            ro = np.array(rays[i].impacts[rays[i].nb_impacts-1]) # ray last coord
            rd = np.array(rays[i].last_direction) # ray direction
            if sensor_type == 'radiance':
                # for radiance sensor, the ray direction values are empty...
                # compute direction from last impact coord
                # note: for radiance sensor, the final impact ("ro") is the sensor vertex
                rd = np.array(rays[i].impacts[rays[i].nb_impacts-2]) - ro # ray last direction

            # check for intersection, and get projection distance
            try:
                hd = np.dot((po - ro), pn) / np.dot(rd, pn)
                if hd < 0:
                    # something went wrong if we are here
                    print('ray couldnt reach sensor')
                    continue
            except:
                # something went wrong if we are here
                print('error: ray couldnt reach sensor')
                continue
            # now check if the intersect coordinate is within our filter area
            sensor_coord = ro + hd*rd
            sensor_coord = sensor_coord - po
            sensor_coord = M.dot(sensor_coord) # change basis to X (left/right), Y (up/down)

            if sensor_type == 'intensity':
                # in this case, look at incident angle rather than coord
                sensor_coord[0] = (180 / np.pi) * np.atan(sensor_coord[0] / far_field_dist)
                sensor_coord[1] = (180 / np.pi) * np.atan(sensor_coord[1] / far_field_dist)

            if (sensor_coord[0] > x-0.5*w) & (sensor_coord[0] < x+0.5*w):
                if (sensor_coord[1] > y-0.5*h) & (sensor_coord[1] < y+0.5*h):
                    filter_idx.append(i)
                    if len(filter_idx) >= num_rays:
                        break

        # manually apply the ray filter
        for i in range(0, len(filter_idx)):
            filtered_lxp.filtered_rays.append(rays[filter_idx[i]])
        
        return filtered_lxp



def run_lxp_viewer(png_path, p, lxp, sensor_obj, sensor_names, sensor_types):
    root = Tk()
    LxpGui(root, png_path, p, lxp, sensor_obj, sensor_names, sensor_types)
    root.mainloop()
