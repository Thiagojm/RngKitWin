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

global thread
thread = False
global index_number_array
index_number_array = []
global zscore_array
zscore_array = []



def main():
    # Mensagem para versão console
    print("""Welcome!
Wait for the application to load!
Do not close this window!""")

    # with open("src/entenda.txt", "r", encoding="utf8") as f:
    #     texto = f.read()

    # THEME
    # Good Ones: BluePurple, BlueMono, DarkBlue9, DarkGrey7, DarkTeal, DarkTeal5, DarkTeal8, LightBlue1, LightBlue2,
    # LightBlue6, LightPurple, Purple
    sg.theme('DarkBlue14')

    # TAB 1 - Capture / Analyse
    acquiring_data = [[sg.T("Choose RNG", size=(20, 1)), sg.T("RAW/XOR", size=(20, 1))],
                     [sg.Radio('BitBabbler', "radio_graph_1", k="bit_ac", default=True, size=(19, 1)),
                      sg.InputCombo((0, 1, 2, 3, 4), default_value=0, size=(4, 1), k="ac_combo", enable_events=False,
                                    readonly=True), sg.T("", size=(2, 1)), sg.B("Start", k='ac_button', size=(20, 1))],
                     [sg.Radio('TrueRNG', "radio_graph_1", k="true3_ac", size=(20, 1))],
                      [sg.Radio('TrueRNG + BitBabbler', "radio_graph_1", k="true3_bit_ac", size=(20, 1))]
                      ]

    data_analysis = [
          [sg.Text('Select file:'), sg.Input(), sg.FileBrowse(key='open_file',
        file_types=(('CSV and Binary', '.csv .bin'),), initial_folder="./1-SavedFiles")],
          [sg.B("Generate")]]

    tab1_layout = [[sg.Frame("Acquiring Data", layout=acquiring_data, k="acquiring_data", size=(90, 9))],
                   [sg.Frame("Data Analysis", layout=data_analysis, k="data_analysis", size=(90, 9))]]

    # TAB 2 - Gráfico
    graph_options = [[sg.T("Choose RNG", size=(20, 1)), sg.T("RAW/XOR", size=(20, 1))],
                     [sg.Radio('BitBabbler', "radio_graph", k="bit_live", default=True, size=(19, 1)),
                      sg.InputCombo((0, 1), default_value=0, size=(4, 1), k="live_combo", enable_events=False,
                                    readonly=True), sg.T("", size=(2, 1)), sg.B("Start", k='live_plot', size=(20, 1))],
                     [sg.Radio('TrueRNG3', "radio_graph", k="true3_live", size=(20, 1))]]

    live_graph = [[sg.Canvas(key='-CANVAS-')]]

    tab2_layout = [[sg.Frame("Options", layout=graph_options, k="graph_options", size=(90, 9))],
                   [sg.Frame("Live Plot", layout=live_graph, k="graph", size=(90, 9))]]

    # TAB 3 - Instruções
    tab3_layout = [[sg.T("Instructions", relief="raised", justification="center", size=(70, 1), font=("Calibri, 24"))],
                   [sg.Multiline(default_text="texto", size=(75, 19), disabled=True, enable_events=False,
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
            print(values)
            ac_data(values, window)
        elif event == "Generate":
            rm.file_to_excel(values["open_file"])
        elif event == 'live_plot':
            global thread
            if not thread:
                thread = True
                ax.clear()
                threading.Thread(target=live_plot, args=(values, window),
                                 daemon=True).start()
                window['live_plot'].update("Stop")
            else:
                thread = False
                window['live_plot'].update("Start")
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
        print("1")
    elif values['true3_ac']:
        print("2")
    elif values["true3_bit_ac"]:
        print("3")

# ----------------Live Plot Functions------------

def live_plot(values, window):
    if values['bit_live']:
        livebblaWin(values, window)
    elif values['true3_live']:
        trng3live(window)

def livebblaWin(values, window):  # Function to take live data from bitbabbler
    global thread
    global zscore_array
    global index_number_array
    thread = True
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    live_combo_value = values['live_combo']
    file_name = time.strftime("%Y%m%d-%H%M%S_bitb_f{}".format(live_combo_value))
    file_name = f"1-SavedFiles/{file_name}"
    index_number = 0
    csv_ones = []
    zscore_array = []
    index_number_array = []
    while thread:
        start_cap = int(time.time() * 1000)
        index_number += 1
        with open(file_name + '.bin', "ab+") as bin_file:  # save binary file
            proc = subprocess.Popen('datafiles/seedd.exe --limit-max-xfer --no-qa -f{} -b 256'.format(live_combo_value),
                                    stdout=subprocess.PIPE, startupinfo=startupinfo)
            chunk = proc.stdout.read()
            bin_file.write(chunk)
        bin_hex = BitArray(chunk)  # bin to hex
        bin_ascii = bin_hex.bin  # hex to ASCII
        if not bin_ascii:
            thread = False
            sg.popup_non_blocking('WARNING !!!',
                                  "Something went wrong, is the device attached? Attach it and try again!!!",
                                  keep_on_top=True, no_titlebar=False, grab_anywhere=True, font="Calibri, 18",
                                  icon="src/BitB.ico")
            window['live_plot'].update("Start")
            break
        num_ones_array = int(bin_ascii.count('1'))  # count numbers of ones in the 2048 string
        csv_ones.append(num_ones_array)
        sums_csv = sum(csv_ones)
        avrg_csv = sums_csv / index_number
        zscore_csv = (avrg_csv - 1024) / (22.62741699796 / (index_number ** 0.5))
        zscore_array.append(zscore_csv)
        index_number_array.append(index_number)
        with open(file_name + '.csv', "a+") as write_file:  # open file and append time and number of ones
            write_file.write('{} {}\n'.format(strftime("%H:%M:%S", localtime()), num_ones_array))
        end_cap = int(time.time() * 1000)
        # print(1 - (end_cap - start_cap) / 1000)
        try:
            time.sleep(1 - (end_cap - start_cap) / 1000)
        except Exception:
            pass


def trng3live(window):
    global thread
    global zscore_array
    global index_number_array
    thread = True
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
    while thread:
        start_cap = int(time.time() * 1000)
        index_number += 1
        with open(file_name + '.bin', "ab+") as bin_file:  # save binary file
            try:
                ser = serial.Serial(port=rng_com_port, timeout=10)  # timeout set at 10 seconds in case the read fails
            except:
                print('Port Not Usable!')
                print('Do you have permissions set to read ' + rng_com_port + ' ?')
            # Open the serial port if it isn't open
            if (ser.isOpen() == False):
                try:
                    ser.open()
                except:
                    thread = False
                    sg.popup_non_blocking('WARNING !!!',
                                          "Something went wrong, is the device attached? Attach it and try again!!!",
                                          keep_on_top=True, no_titlebar=False, grab_anywhere=True, font="Calibri, 18",
                                          icon="src/BitB.ico")
                    window['live_plot'].update("Start")
                    return
            # Set Data Terminal Ready to start flow
            ser.setDTR(True)
            # This clears the receive buffer so we aren't using buffered data
            ser.flushInput()
            try:
                chunk = ser.read(blocksize)  # read bytes from serial port
            except:
                print('Read Failed!!!')  # If we were able to open the file, write to disk
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
        end_cap = int(time.time() * 1000)
        # print(1 - (end_cap - start_cap) / 1000)
        try:
            time.sleep(1 - (end_cap - start_cap) / 1000)
        except Exception:
            pass


if __name__ == '__main__':
    main()
