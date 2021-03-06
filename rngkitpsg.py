# Default imports
import time
import threading
import subprocess
from time import localtime, strftime

# External imports
import pandas as pd
import PySimpleGUI as sg
import matplotlib.pyplot as plt
from matplotlib import style
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from bitstring import BitArray
import serial
from serial.tools import list_ports

# Internal imports
import rng_module as rm

global thread_live
thread_live = False
global thread_cap
thread_cap = False
global index_number_array
index_number_array = []
global zscore_array
zscore_array = []


def main():
    # Mensagem para versão console
    print("""Welcome!
Wait for the application to load!
Do not close this window!""")

    with open("src/instructions.txt", "r", encoding="utf8") as f:
        texto = f.read()

    # THEME
    # Good Ones: DarkBlue14, Dark, DarkBlue, DarkBlue3, DarkTeal1, DarkTeal10, DarkTeal9, LightGreen
    sg.theme('DarkBlue')

    # TAB 1 - Capture / Analyse
    acquiring_data = [[sg.T("Choose RNG", size=(16, 1)), sg.T("RAW(0)/XOR(1,2...)", size=(20, 1))],
                      [sg.Radio('BitBabbler', "radio_graph_1", k="bit_ac", default=True, size=(19, 1)),
                       sg.InputCombo((0, 1, 2, 3, 4), default_value=0, size=(4, 1), k="ac_combo", enable_events=False,
                                     readonly=True), sg.T("", size=(4, 1)), sg.B("Start", k='ac_button', size=(20, 1))],
                      [sg.Radio('TrueRNG', "radio_graph_1", k="true3_ac", size=(36, 1)),
                       sg.T("        Idle", k="stat_ac", text_color="orange", size=(10, 1), relief="sunken")],
                      [sg.Radio('TrueRNG + BitBabbler', "radio_graph_1", k="true3_bit_ac", size=(20, 1))]]

    data_analysis = [[sg.Text('Select file:'), sg.Input(),
                      sg.FileBrowse(key='open_file', file_types=(('CSV and Binary', '.csv .bin'),),
                                    initial_folder="./1-SavedFiles")],
                     [sg.B("Generate"), sg.B("Open Output Folder", k="out_folder")]]

    tab1_layout = [[sg.Frame("Acquiring Data", layout=acquiring_data, k="acquiring_data", size=(90, 9))],
                   [sg.Frame("Data Analysis", layout=data_analysis, k="data_analysis", size=(90, 9))]]

    # TAB 2 - Gráfico
    graph_options = [[sg.T("Choose RNG", size=(20, 1)), sg.T("RAW/XOR", size=(20, 1))],
                     [sg.Radio('BitBabbler', "radio_graph", k="bit_live", default=True, size=(19, 1)),
                      sg.InputCombo((0, 1), default_value=0, size=(4, 1), k="live_combo", enable_events=False,
                                    readonly=True), sg.T("", size=(2, 1)), sg.B("Start", k='live_plot', size=(20, 1))],
                     [sg.Radio('TrueRNG3', "radio_graph", k="true3_live", size=(20, 1)),
                      sg.T("        Idle", k="stat_live", text_color="orange", size=(10, 1), relief="sunken")]]

    live_graph = [[sg.Canvas(key='-CANVAS-')]]

    tab2_layout = [[sg.Frame("Options", layout=graph_options, k="graph_options", size=(90, 9))],
                   [sg.Frame("Live Plot", layout=live_graph, k="graph", size=(90, 9))]]

    # TAB 3 - Instruções
    tab3_layout = [[sg.T("Instructions", relief="raised", justification="center", size=(70, 1), font=("Calibri, 24"))],
                   [sg.Multiline(default_text=texto, size=(75, 19), disabled=True, enable_events=False,
                                 font=("Calibri, 20"), pad=(5, 5))]]

    # LAYOUT
    layout = [[sg.TabGroup(
        [[sg.Tab('Start', tab1_layout), sg.Tab('Live Plot', tab2_layout), sg.Tab('Instructions', tab3_layout)]],
        tab_location="top", font="Calibri, 18")]]

    # WINDOW
    window = sg.Window("RngKit ver 2.0.0 - by Thiago Jung", layout, size=(1024, 720), location=(50, 50), finalize=True,
                       element_justification="center", font="Calibri 18", resizable=True, icon=("src/BitB.ico"))

    # Setting things up!
    canvas_elem = window['-CANVAS-']
    canvas = canvas_elem.TKCanvas
    # draw the intitial plot
    style.use("ggplot")
    fig, ax = plt.subplots(figsize=(10, 5), dpi=100)
    fig_agg = rm.draw_figure(canvas, fig)

    # LOOP
    while True:
        event, values = window.read(timeout=200)
        if event == sg.WIN_CLOSED:  # always,  always give a way out!
            break
        elif event == 'ac_button':
            global thread_cap
            if not thread_cap:
                thread_cap = True
                threading.Thread(target=ac_data, args=(values, window), daemon=True).start()
                window['ac_button'].update("Stop")
                window["stat_ac"].update("  Capturing", text_color="green")
            else:
                thread_cap = False
                window['ac_button'].update("Start")
                window["stat_ac"].update("        Idle", text_color="orange")
        elif event == "out_folder":
            rm.open_folder()
        elif event == "Generate":
            rm.file_to_excel(values["open_file"])
        elif event == 'live_plot':
            global thread_live
            if not thread_live:
                thread_live = True
                ax.clear()
                threading.Thread(target=live_plot, args=(values, window), daemon=True).start()
                window['live_plot'].update("Stop")
                window["stat_live"].update("  Capturing", text_color="green")
            else:
                thread_live = False
                window['live_plot'].update("Start")
                window["stat_live"].update("        Idle", text_color="orange")
        # Live Plot on Loop
        ax.plot(index_number_array, zscore_array, color='orange')
        ax.set_title("Live Plot")
        ax.set_xlabel('Time(s)', fontsize=10)
        ax.set_ylabel('Z-Score', fontsize='medium')
        fig_agg.draw()
    window.close()


# ---------------- Acquire Data Functions -------
def ac_data(values, window):
    if values["bit_ac"]:
        bit_cap(values, window)
    elif values['true3_ac']:
        trng3_cap(window)
    elif values["true3_bit_ac"]:
        threading.Thread(target=bit_cap, args=(values, window), daemon=True).start()
        trng3_cap(window)


def bit_cap(values, window):  # criar função para quando o botão for clicado
    xor_value = values["ac_combo"]
    global thread_cap
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    file_name = time.strftime("%Y%m%d-%H%M%S_bitb_f{}".format(xor_value))
    file_name = f"1-SavedFiles/{file_name}"
    while thread_cap:
        start_cap = time.time()
        with open(file_name + '.bin', "ab+") as bin_file:  # save binary file
            proc = subprocess.run(f'datafiles/seedd.exe --limit-max-xfer --no-qa -f{xor_value} -b 256',
                                  stdout=subprocess.PIPE)
            chunk = proc.stdout
            bin_file.write(chunk)
        bin_hex = BitArray(chunk)  # bin to hex
        bin_ascii = bin_hex.bin  # hex to ASCII
        if not bin_ascii:
            thread_cap = False
            sg.popup_non_blocking('WARNING !!!',
                                  "Something went wrong, is the device attached? Attach it and try again!!!",
                                  keep_on_top=True, no_titlebar=False, grab_anywhere=True, font="Calibri, 18",
                                  icon="src/BitB.ico")
            window['ac_button'].update("Start")
            window["stat_ac"].update("        Idle", text_color="orange")
            break
        num_ones_array = bin_ascii.count('1')  # count numbers of ones in the 2048 string
        with open(file_name + '.csv', "a+") as write_file:  # open file and append time and number of ones
            write_file.write('{} {}\n'.format(strftime("%H:%M:%S", localtime()), num_ones_array))
        end_cap = time.time()
        # print(1 - (end_cap - start_cap))
        try:
            time.sleep(1 - (end_cap - start_cap))
        except Exception:
            pass


def trng3_cap(window):
    global thread_cap
    blocksize = 256
    ports = dict()
    ports_avaiable = list(list_ports.comports())
    rng_com_port = None
    for temp in ports_avaiable:
        if temp[1].startswith("TrueRNG"):
            if rng_com_port == None:  # always chooses the 1st TrueRNG found
                rng_com_port = str(temp[0])
    file_name = time.strftime("%Y%m%d-%H%M%S_trng")
    file_name = f"1-SavedFiles/{file_name}"
    while thread_cap:
        start_cap = time.time()
        with open(file_name + '.bin', "ab") as bin_file:  # save binary file
            try:
                ser = serial.Serial(port=rng_com_port, timeout=10)  # timeout set at 10 seconds in case the read fails
                if (ser.isOpen() == False):
                    ser.open()
                ser.setDTR(True)
                ser.flushInput()
            except Exception:
                rm.popupmsg("Warning!", f"Port Not Usable! Do you have permissions set to read {rng_com_port}?")
                thread_cap = False
                window['ac_button'].update("Start")
                window["stat_ac"].update("        Idle", text_color="orange")
                break
            try:
                x = ser.read(blocksize)  # read bytes from serial port
            except Exception:
                rm.popupmsg("Warning!", "Read failed!")
                thread_cap = False
                window['ac_button'].update("Start")
                window["stat_ac"].update("        Idle", text_color="orange")
                break
            if bin_file != 0:
                bin_file.write(x)
            ser.close()
            if bin_file != 0:
                bin_file.close()
        bin_hex = BitArray(x)  # bin to hex
        bin_ascii = bin_hex.bin  # hex to ASCII
        num_ones_array = bin_ascii.count('1')  # count numbers of ones in the 2048 string
        with open(file_name + '.csv', "a+") as write_file:  # open file and append time and number of ones
            write_file.write('{} {}\n'.format(strftime("%H:%M:%S", localtime()), num_ones_array))
        end_cap = time.time()
        # print(1 - (end_cap - start_cap))
        try:
            time.sleep(1 - (end_cap - start_cap))
        except Exception:
            pass


# ----------------Live Plot Functions------------

def live_plot(values, window):
    if values['bit_live']:
        livebblaWin(values, window)
    elif values['true3_live']:
        trng3live(window)


def livebblaWin(values, window):  # Function to take live data from bitbabbler
    global thread_live
    global zscore_array
    global index_number_array
    thread_live = True
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    live_combo_value = values['live_combo']
    file_name = time.strftime("%Y%m%d-%H%M%S_bitb_f{}".format(live_combo_value))
    file_name = f"1-SavedFiles/{file_name}"
    index_number = 0
    csv_ones = []
    zscore_array = []
    index_number_array = []
    while thread_live:
        start_cap = time.time()
        index_number += 1
        with open(file_name + '.bin', "ab+") as bin_file:  # save binary file
            proc = subprocess.run(f'datafiles/seedd.exe --limit-max-xfer --no-qa -f{live_combo_value} -b 256',
                                  stdout=subprocess.PIPE)
            chunk = proc.stdout
            bin_file.write(chunk)
        bin_hex = BitArray(chunk)  # bin to hex
        bin_ascii = bin_hex.bin  # hex to ASCII
        if not bin_ascii:
            thread_live = False
            sg.popup_non_blocking('WARNING !!!',
                                  "Something went wrong, is the device attached? Attach it and try again!!!",
                                  keep_on_top=True, no_titlebar=False, grab_anywhere=True, font="Calibri, 18",
                                  icon="src/BitB.ico")
            window['live_plot'].update("Start")
            window["stat_live"].update("        Idle", text_color="orange")
            break
        num_ones_array = bin_ascii.count('1')  # count numbers of ones in the 2048 string
        csv_ones.append(num_ones_array)
        sums_csv = sum(csv_ones)
        avrg_csv = sums_csv / index_number
        zscore_csv = (avrg_csv - 1024) / (22.62741699796 / (index_number ** 0.5))
        zscore_array.append(zscore_csv)
        index_number_array.append(index_number)
        with open(file_name + '.csv', "a+") as write_file:  # open file and append time and number of ones
            write_file.write('{} {}\n'.format(strftime("%H:%M:%S", localtime()), num_ones_array))
        end_cap = time.time()
        # print(1 - (end_cap - start_cap))
        try:
            time.sleep(1 - (end_cap - start_cap))
        except Exception:
            pass


def trng3live(window):
    global thread_live
    global zscore_array
    global index_number_array
    thread_live = True
    file_name = time.strftime("%Y%m%d-%H%M%S_trng")
    file_name = f"1-SavedFiles/{file_name}"
    index_number = 0
    csv_ones = []
    zscore_array = []
    index_number_array = []
    blocksize = 256
    ports_avaiable = list(list_ports.comports())
    rng_com_port = None
    # Loop on all available ports to find TrueRNG
    for temp in ports_avaiable:
        if temp[1].startswith("TrueRNG"):
            if rng_com_port == None:  # always chooses the 1st TrueRNG found
                rng_com_port = str(temp[0])
    while thread_live:
        start_cap = time.time()
        index_number += 1
        with open(file_name + '.bin', "ab+") as bin_file:  # save binary file
            try:
                ser = serial.Serial(port=rng_com_port, timeout=10)  # timeout set at 10 seconds in case the read fails
            except Exception:
                thread_live = False
                rm.popupmsg("Warning!", f"Port Not Usable! Do you have permissions set to read {rng_com_port}?")
                window['live_plot'].update("Start")
                window["stat_live"].update("        Idle", text_color="orange")
                return
            # Open the serial port if it isn't open
            if (ser.isOpen() == False):
                try:
                    ser.open()
                except Exception:
                    thread_live = False
                    sg.popup_non_blocking('WARNING !!!',
                                          "Something went wrong, is the device attached? Attach it and try again!!!",
                                          keep_on_top=True, no_titlebar=False, grab_anywhere=True, font="Calibri, 18",
                                          icon="src/BitB.ico")
                    window['live_plot'].update("Start")
                    window["stat_live"].update("        Idle", text_color="orange")
                    return
            # Set Data Terminal Ready to start flow
            ser.setDTR(True)
            # This clears the receive buffer so we aren't using buffered data
            ser.flushInput()
            try:
                chunk = ser.read(blocksize)  # read bytes from serial port
            except Exception:
                thread_live = False
                rm.popupmsg("Warning!", "Read Failed!!!")
                window['live_plot'].update("Start")
                window["stat_live"].update("        Idle", text_color="orange")
                return
            if bin_file != 0:
                bin_file.write(chunk)
            # Close the serial port
            ser.close()
        bin_hex = BitArray(chunk)  # bin to hex
        bin_ascii = bin_hex.bin  # hex to ASCII
        num_ones_array = int(bin_ascii.count('1'))  # count numbers of ones in the 2048 string
        csv_ones.append(num_ones_array)
        sums_csv = sum(csv_ones)
        avrg_csv = sums_csv / index_number
        zscore_csv = (avrg_csv - 1024) / (22.62741699796 / (index_number ** 0.5))
        zscore_array.append(zscore_csv)
        index_number_array.append(index_number)
        with open(file_name + '.csv', "a+") as write_file:  # open file and append time and number of ones
            write_file.write('{} {}\n'.format(strftime("%H:%M:%S", localtime()), num_ones_array))
        end_cap = time.time()
        # print(1 - (end_cap - start_cap) / 1000)
        try:
            time.sleep(1 - (end_cap - start_cap))
        except Exception:
            pass


if __name__ == '__main__':
    main()
