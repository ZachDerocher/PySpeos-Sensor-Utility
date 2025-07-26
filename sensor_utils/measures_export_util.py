import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import ansys.speos.core.workflow.open_result as orf

def insert_header(original_file, header_string):
    """
    add a header line above the first line of a text file
    """
    with open(original_file,'r') as f:
        new_file = original_file[0:-4] + '_header.txt'
        with open(new_file,'w') as f2: 
            f2.write(header_string + "\n")
            f2.write(f.read())
    return new_file


def render_mpl_table(data, col_width=3.0, row_height=0.625, font_size=14,
                header_color='#40466e', row_colors=['#f1f1f2', 'w'], edge_color='w',
                bbox=[0, 0, 1, 1], header_columns=0,
                ax=None, **kwargs):
        """
        plots a pandas df via matplotlib, with some basic formatting
        """
        if ax is None:
                size = (np.array(data.shape[::-1]) + np.array([0, 1])) * np.array([col_width, row_height])
                fig, ax = plt.subplots(figsize=size)
                ax.axis('off')
        mpl_table = ax.table(cellText=data.values, bbox=bbox, colLabels=data.columns, **kwargs)
        mpl_table.auto_set_font_size(False)
        mpl_table.set_fontsize(font_size)
        
        for row in range(0,data.shape[0]):
                rule_check = data.l[row]
                if rule_check == 'RuleStatus=(passed)':
                        mpl_table[(row-1, 0)].set_facecolor('lime')
                        mpl_table[(row+1, 11)].set_facecolor('lime')
                elif rule_check == 'RuleStatus=(failed)':
                        mpl_table[(row-1, 0)].set_facecolor('orangered')
                        mpl_table[(row+1, 11)].set_facecolor('orangered')

        return ax.get_figure(), ax



def measures_export(sim, sensor):
        """
        retrieve the xmp measures, save as text, and then export as formatted table
        inputs:
                sim : the pyspeos simulation
                sensor : the pyspeos sensor object for which measures will be exported
        outputs:
                the path to the exported table image file
        """
        result_name = sensor.get("result_file_name")
        xmp_path = orf._find_correct_result(sim, result_name + ".xmp")
        if os.name == "nt":
                from comtypes.client import CreateObject
        dpf_instance = CreateObject("XMPViewer.Application")
        dpf_instance.OpenFile(xmp_path)
        measures_path = xmp_path[0:-3] + 'txt'
        dpf_instance.MeasuresExportTXT(measures_path)

        header = "a\tb\tc\td\te\tf\tg\th\ti\tj\tk\tl\tm\tn\to\tp" # the data has 16 columns
        tmp_txt = insert_header(measures_path, header)

        measures = pd.read_csv(tmp_txt, sep='\t', skiprows=0, header=0, na_filter=False)
        measures.to_string()
        os.remove(tmp_txt)
                
        fig,ax = render_mpl_table(measures, header_columns=0, col_width=5.0)
        out_png = "table_mpl.png"
        fig.savefig(out_png)
        return out_png


if __name__=="__main__":

        header = "a\tb\tc\td\te\tf\tg\th\ti\tj\tk\tl\tm\tn\to\tp"
        tmp_txt = insert_header("tmp_measures.txt", header)

        measures = pd.read_csv(tmp_txt, sep='\t', skiprows=0, header=0, na_filter=False)
        measures.to_string()
        os.remove(tmp_txt)
                
        fig,ax = render_mpl_table(measures, header_columns=0, col_width=5.0)
        fig.savefig("table_mpl.png")
