# Default imports
import os
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
from textwrap import wrap
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

    # with open("src/entenda.txt", "r", encoding="utf8") as f:
    #     texto = f.read()

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
    x = None
    # draw the intitial plot
    style.use("ggplot")
    fig, ax = plt.subplots(figsize=(10, 5), dpi=100)
    fig_agg = rm.draw_figure(canvas, fig)

    # LOOP
    while True:
        event, values = window.read(timeout=100)
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
            x = threading.Thread(target=file_to_excel, args=(values["open_file"], window), daemon=True)
            x.start()
            # rm.file_to_excel(values["open_file"])
        elif event == 'live_plot':
            global thread_live
            if not thread_live:
                thread_live = True
                ax.clear()
                threading.Thread(target=live_plot, args=(values, window), daemon=True).start()
                window['live_plot'].update("Stop")
            else:
                thread_live = False
                window['live_plot'].update("Start")
        elif event == '-THREAD-':  # Thread has completed
            x.join(timeout=0)
            print('Thread finished')
            sg.popup_animated(None)  # stop animination in case one is running
            x = None
        if x is not None:
            sg.popup_animated(sg.DEFAULT_BASE64_LOADING_GIF, background_color='white', transparent_color='white',
                              time_between_frames=100)
        # Live Plot on Loop
        ax.plot(index_number_array, zscore_array, color='orange')
        ax.set_title("Live Plot")
        ax.set_xlabel('Time(s)', fontsize=10)
        ax.set_ylabel('Z-Score', fontsize='medium')
        fig_agg.draw()
    window.close()


def check_thread():
    global x
    while x.is_alive():
        sg.popup_animated(sg.DEFAULT_BASE64_LOADING_GIF, 'Loading list of packages', time_between_frames=100)
        x.join(timeout=.1)
        if not x.is_alive():
            break
    sg.popup_animated(None)


def file_to_excel(data_file, window):
    if data_file == "":
        sg.popupmsg('Atention', 'Select a file first')
        pass
    elif data_file[-3:] == "csv":
        ztest = ztest_pandas(data_file)
        data_file2 = os.path.basename(data_file)
        data_file2 = data_file2.replace(".csv", "")
        file_to_save = data_file.replace(".csv", ".xlsx")
        number_rows = len(ztest.index)
        writer = pd.ExcelWriter(file_to_save, engine='xlsxwriter')
        ztest.to_excel(writer, sheet_name='Z-Test', index=False)
        workbook = writer.book
        worksheet = writer.sheets['Z-Test']
        chart = create_chart(workbook, data_file2)
        chart.add_series({'values': ['Z-Test', 1, 5, number_rows, 5], 'categories': ['Z-Test', 1, 1, number_rows, 1]})
        worksheet.insert_chart('G2', chart)
        writer.save()
        sg.popupmsg('File Saved', 'Saved as ' + file_to_save)
        return
    elif data_file[-3:] == "bin":
        # sg.PopupQuickMessage("Working, please wait... this could take many seconds.", background_color="Grey",
        #                      font="Calibri, 18", auto_close_duration=2)
        num_ones_array = []
        with open(data_file, "rb") as file:  # open binary file
            bin_hex = BitArray(file)  # bin to hex
        bin_ascii = bin_hex.bin
        split_bin_ascii = wrap(bin_ascii, 2048)  # split in 2048 bits per line - 1 second

        num_ones_array = bin_stuff(num_ones_array, split_bin_ascii)

        binSheet = binary_data(num_ones_array)
        data_file2 = os.path.basename(data_file)
        data_file2 = data_file2.replace(".bin", "")
        file_to_save = data_file.replace(".bin", ".xlsx")
        number_rows = len(binSheet.Time)
        writer = pd.ExcelWriter(file_to_save, engine='xlsxwriter')
        binSheet.to_excel(writer, sheet_name='Z-Test', index=False)
        workbook = writer.book
        worksheet = writer.sheets['Z-Test']

        chart = create_chart(workbook, data_file2)
        chart.add_series({'values': ['Z-Test', 1, 4, number_rows, 4], 'categories': ['Z-Test', 1, 0, number_rows, 0]})
        worksheet.insert_chart('G2', chart)
        writer.save()
        sg.PopupQuickMessage('File Saved', 'Saved as ' + file_to_save)
        window.write_event_value('-THREAD-', '*** The thread says.... "I am finished" ***')
        return
    else:
        sg.PopupQuickMessage("Warning", 'Wrong File Type, Select a .bin or .csv file')
        pass


def binary_data(num_ones_array):
    binSheet = pd.DataFrame()  # Array to Pandas Column
    binSheet['Ones'] = num_ones_array
    binSheet.dropna(inplace=True)
    binSheet = binSheet.reset_index()
    binSheet['index'] = binSheet['index'] + 1
    binSheet = binSheet.rename(columns={'index': 'Time'})
    binSheet['Sum'] = binSheet['Ones'].cumsum()
    binSheet['Average'] = binSheet['Sum'] / (binSheet['Time'])
    binSheet['Zscore'] = (binSheet['Average'] - 1024) / (22.62741699796 / (binSheet['Time'] ** 0.5))
    return binSheet


def bin_stuff(num_ones_array, split_bin_ascii):
    for i in split_bin_ascii:  # calculate number of 'ones' in each of the 2048 bits lines
        num_ones_array.append(i.count('1'))
    return num_ones_array


def create_chart(workbook, data_file2):
    chart = workbook.add_chart({'type': 'line'})
    chart.set_title({'name': 'Z-Score: ' + data_file2, 'name_font': {'name': 'Calibri', 'color': 'black', }, })

    chart.set_x_axis({'name': 'Time', 'name_font': {'name': 'Calibri', 'color': 'black'},
                      'num_font': {'name': 'Calibri', 'color': 'black', }, })

    chart.set_y_axis(
        {'name': 'Z-Score', 'name_font': {'name': 'Calibri', 'color': 'black'}, 'num_font': {'color': 'black', }, })

    chart.set_legend({'position': 'none'})
    return chart


def ztest_pandas(data_file):
    ztest = pd.read_csv(data_file, sep=' ', names=["Time", "Ones"])
    ztest.dropna(inplace=True)
    ztest = ztest.reset_index()
    ztest['index'] = ztest['index'] + 1
    ztest['Sum'] = ztest['Ones'].cumsum()
    ztest['Average'] = ztest['Sum'] / (ztest['index'])
    ztest['Zscore'] = (ztest['Average'] - 1024) / (22.62741699796 / (ztest['index'] ** 0.5))
    return ztest


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
        start_cap = int(time.time() * 1000)
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
        end_cap = int(time.time() * 1000)
        # print(1 - (end_cap - start_cap)/1000)
        try:
            time.sleep(1 - (end_cap - start_cap) / 1000)
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
        start_cap = int(time.time() * 1000)
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
        end_cap = int(time.time() * 1000)
        # print(1 - (end_cap - start_cap) / 1000)
        try:
            time.sleep(1 - (end_cap - start_cap) / 1000)
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
        start_cap = int(time.time() * 1000)
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
        end_cap = int(time.time() * 1000)
        # print(1 - (end_cap - start_cap) / 1000)
        try:
            time.sleep(1 - (end_cap - start_cap) / 1000)
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
        start_cap = int(time.time() * 1000)
        index_number += 1
        with open(file_name + '.bin', "ab+") as bin_file:  # save binary file
            try:
                ser = serial.Serial(port=rng_com_port, timeout=10)  # timeout set at 10 seconds in case the read fails
            except Exception:
                thread_live = False
                rm.popupmsg("Warning!", f"Port Not Usable! Do you have permissions set to read {rng_com_port}?")
                window['live_plot'].update("Start")
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
        end_cap = int(time.time() * 1000)
        # print(1 - (end_cap - start_cap) / 1000)
        try:
            time.sleep(1 - (end_cap - start_cap) / 1000)
        except Exception:
            pass


if __name__ == '__main__':
    main()
