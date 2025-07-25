import os
from tabulate import tabulate
import pandas as pd
from pandas.plotting import table
import numpy as np
import matplotlib.pyplot as plt
import csv
import ansys.speos.core.workflow.open_result as orf


def measures_export(sim, sensor):

        result_name = sensor.get("result_file_name")
        xmp_path = orf._find_correct_result(sim, result_name + ".xmp")
        if os.name == "nt":
                from comtypes.client import CreateObject
        dpf_instance = CreateObject("XMPViewer.Application")
        dpf_instance.OpenFile(xmp_path)
        measures_path = xmp_path[0:-3] + 'txt'
        dpf_instance.MeasuresExportTXT(measures_path)
        measures = pd.read_csv(measures_path, sep='\t', header=2)
        t = measures.style
        print('hi')


def render_mpl_table(data, col_width=3.0, row_height=0.625, font_size=14,
                header_color='#40466e', row_colors=['#f1f1f2', 'w'], edge_color='w',
                bbox=[0, 0, 1, 1], header_columns=0,
                ax=None, **kwargs):
        if ax is None:
                size = (np.array(data.shape[::-1]) + np.array([0, 1])) * np.array([col_width, row_height])
                fig, ax = plt.subplots(figsize=size)
                ax.axis('off')
        mpl_table = ax.table(cellText=data.values, bbox=bbox, colLabels=data.columns, **kwargs)
        mpl_table.auto_set_font_size(False)
        mpl_table.set_fontsize(font_size)
        """
        for k, cell in mpl_table._cells.items():
                cell.set_edgecolor(edge_color)
                if k[0] == 0 or k[1] < header_columns:
                        cell.set_text_props(weight='bold', color='w')
                        cell.set_facecolor(header_color)
                else:
                        cell.set_facecolor(row_colors[k[0]%len(row_colors) ])
        """
        return ax.get_figure(), ax



if __name__=="__main__":
        col_names = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p"]
        measures = pd.read_csv("tmp_measures.txt", sep='\t', header=2, na_filter=False, names=col_names)
        measures.to_string()

                
        fig,ax = render_mpl_table(measures, header_columns=0, col_width=6.0)
        fig.savefig("table_mpl.png")

        #measures = measures.replace(np.nan,' ', regex=True)
        #t = measures.style
        #print('here')

        # Replace 'file.tsv' with the path to your tab-separated file
        #with open("tmp_measures.txt", 'r') as file:
        #        reader = csv.reader(file, delimiter='\t')
        #        data = [row for row in reader]

        #print(tabulate(data))


        #print(data)

