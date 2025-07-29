import os

def export_result_iso_curve(xmp_path):
    # create a pretty iso plot for intensity sensor
    
    if os.name == "nt":
        from comtypes.client import CreateObject
    dpf_instance = CreateObject("XMPViewer.Application")
    dpf_instance.OpenFile(xmp_path)

    png_path = xmp_path[0:-4] + '.png'
    png_path_isolevel = xmp_path[0:-4] + '_isolevels.png'

    dpf_instance.ExportXMPImage(png_path, 1)
    dpf_instance.SetColorMode(10)
    dpf_instance.IsoCurves(1)
    dpf_instance.ShowPrimaryGrid(True)
    dpf_instance.ExportXMPImage(png_path_isolevel, 1)

    # Close XMPViewer
    pid=dpf_instance.GetPID
    cmd = 'taskkill /PID ' + str(pid) + ' /F'
    os.system(cmd)

    return png_path, png_path_isolevel