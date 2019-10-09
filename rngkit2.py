import matplotlib

matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import matplotlib.animation as animation
from matplotlib import style
from matplotlib import pyplot as plt
import tkinter as tk
from tkinter import ttk
import pandas as pd
from tkinter import filedialog
import tkinter.messagebox
import os
import time
from time import localtime, strftime
import subprocess
from PIL import Image, ImageTk
import threading
from bitstring import BitArray
from textwrap import wrap
import serial
from serial.tools import list_ports

LARGE_FONT = ("Verdana", 12)
style.use("ggplot")

f = Figure(figsize=(10, 5), dpi=100)
a = f.add_subplot(111)
index_number_array = []
zscore_array = []

def animate(i):
    xar = index_number_array
    yar = zscore_array
    a.clear()
    #a.grid()
    a.plot(xar, yar, color='orange')
    # ax1.tick_params(axis='x', rotation=45)
    a.set_title("Live Plot")
    # ax1.set_xticks(ax1.get_xticks()[::5])


class rngKit(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        tk.Tk.iconbitmap(self)
        tk.Tk.wm_title(self, "RngKit for Windows")

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (StartPage, PageOne, PageTwo, PageThree):
            frame = F(container, self)

            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()


class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Start Page", font=LARGE_FONT)
        label.pack(pady=10, padx=10)

        button = ttk.Button(self, text="Visit Page 1",
                            command=lambda: controller.show_frame(PageOne))
        button.pack()

        button2 = ttk.Button(self, text="Visit Page 2",
                             command=lambda: controller.show_frame(PageTwo))
        button2.pack()

        button3 = ttk.Button(self, text="Graph Page",
                             command=lambda: controller.show_frame(PageThree))
        button3.pack()


class PageOne(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Page One!!!", font=LARGE_FONT)
        label.pack(pady=10, padx=10)

        button1 = ttk.Button(self, text="Back to Home",
                             command=lambda: controller.show_frame(StartPage))
        button1.pack()

        button2 = ttk.Button(self, text="Page Two",
                             command=lambda: controller.show_frame(PageTwo))
        button2.pack()


class PageTwo(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Page Two!!!", font=LARGE_FONT)
        label.pack(pady=10, padx=10)

        button1 = ttk.Button(self, text="Back to Home",
                             command=lambda: controller.show_frame(StartPage))
        button1.pack()

        button2 = ttk.Button(self, text="Page One",
                             command=lambda: controller.show_frame(PageOne))
        button2.pack()


class PageThree(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Live Plot", font=LARGE_FONT)
        label.pack(pady=10, padx=10)
        global script_path
        global isLiveOn
        global selectedLive
        script_path = os.getcwd()
        isCapturingOn = False
        isLiveOn = False

        def livebblaWin():  # Function to take live data from bitbabbler
            global isLiveOn
            global zscore_array
            global index_number_array
            isLiveOn = True
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            selectedComboLive = comboBLive.get()
            file_name = time.strftime("%Y%m%d-%H%M%S_bitb_f{}".format(selectedComboLive))
            index_number = 0
            csv_ones = []
            zscore_array = []
            index_number_array = []
            while isLiveOn:
                start_cap = int(time.time() * 1000)
                index_number += 1
                with open(file_name + '.bin', "ab+") as bin_file:  # save binary file
                    proc = subprocess.Popen('seedd.exe --limit-max-xfer --no-qa -f{} -b 256'.format(selectedComboLive),
                                            stdout=subprocess.PIPE, startupinfo=startupinfo)
                    chunk = proc.stdout.read()
                    bin_file.write(chunk)
                bin_hex = BitArray(chunk)  # bin to hex
                bin_ascii = bin_hex.bin  # hex to ASCII
                if not bin_ascii:
                    isLiveOn = False
                    tk.messagebox.showinfo('WARNING !!! ',
                                           'Something went wrong, is the device attached? Attach it and restart the program!!!')
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

        def trng3live():
            global isLiveOn
            global zscore_array
            global index_number_array
            isLiveOn = True
            file_name = time.strftime("%Y%m%d-%H%M%S_trng")
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
            while isLiveOn:
                start_cap = int(time.time() * 1000)
                index_number += 1
                with open(file_name + '.bin', "ab+") as bin_file:  # save binary file
                    try:
                        ser = serial.Serial(port=rng_com_port,
                                            timeout=10)  # timeout set at 10 seconds in case the read fails
                    except:
                        print('Port Not Usable!')
                        print('Do you have permissions set to read ' + rng_com_port + ' ?')
                    # Open the serial port if it isn't open
                    if (ser.isOpen() == False):
                        try:
                            ser.open()
                        except:
                            isLiveOn = False
                            tk.messagebox.showinfo('WARNING !!! ',
                                                   'Something went wrong, is the device attached? Attach it and restart the program!!!')
                            return
                    # Set Data Terminal Ready to start flow
                    ser.setDTR(True)
                    # This clears the receive buffer so we aren't using buffered data
                    ser.flushInput()
                    try:
                        chunk = ser.read(blocksize)  # read bytes from serial port
                    except:
                        print('Read Failed!!!')
                        # If we were able to open the file, write to disk
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


        def livePlot():
            global selectedLive
            global isLiveOn
            if isLiveOn == True:
                tk.messagebox.showinfo('WARNING !!! ', ' Press Stop before starting new Plot')
                return
            else:
                if selectedLive.get() == 1:  # start Bitbabbler live
                    threading.Thread(target=livebblaWin).start()
                elif selectedLive.get() == 2:  # start TrueRNG live
                    threading.Thread(target=trng3live).start()


        def stopLive():
            global isLiveOn
            if isLiveOn == True:
                isLiveOn = False
                #ani.event_source.stop()
                tk.messagebox.showinfo('File Saved','Saved as ' + file_to_save)
            else:
                tk.messagebox.showinfo('Alert', 'Capure not started')


        # Radiobuttons/ Combobox
        selectedLive = tk.IntVar()
        selectedLive.set(1)
        selectedComboLive = tk.StringVar()

        # Frame 1
        frame1 = tk.Frame(self)
        frame1.pack(fill="x")
        lbl30 = tk.Label(frame1, text="Choose RNG",
                         font=("Arial Bold", 11),
                         padx=5, pady=5)  # Text inside window
        lbl30.pack(side="left", padx=5, pady=5)  # posição do label

        lbl31 = tk.Label(frame1, text="RAW/XOR",
                         font=("Arial Bold", 11),
                         padx=5, pady=5)  # Text inside window
        lbl31.pack(side="left", padx=5, pady=5)  # posição do label


        # Frame 2
        frame2 = tk.Frame(self)
        frame2.pack(fill="x")
        radBlive = tk.ttk.Radiobutton(frame2, text='Bitbabbler           ', value=1, variable=selectedLive)
        radBlive.pack(side="left", padx=5, pady=5)
        comboBLive = ttk.Combobox(frame2, width=3)
        comboBLive['values'] = (0, 1)
        comboBLive.current(0)
        comboBLive.pack(side="left", padx=5, pady=5)
        btn31 = tk.Button(frame2, text="Live Plot", bg="white", fg="blue",
                          command=livePlot,
                          padx=5, pady=5)  # criar botão/ command=função do botão
        btn31.pack(side="left", padx=30, pady=5)


        # Frame 3
        frame3 = tk.Frame(self)
        frame3.pack(fill="x")
        radTrngLive = tk.ttk.Radiobutton(frame3, text='TrueRng                               ', value=2, variable=selectedLive)
        radTrngLive.pack(side="left", padx=5, pady=5)
        btn32 = tk.Button(frame3, text="Stop", bg="white", fg="blue",
                          command=stopLive,
                          padx=5, pady=5)  # criar botão/ command=função do botão
        btn32.pack(side="left", padx=30, pady=5)

        # Frame 4
        frame4 = tk.Frame(self)
        frame4.pack(fill="both", pady=5, padx=5, expand=True)

        canvas = FigureCanvasTkAgg(f, frame4)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        toolbar = NavigationToolbar2Tk(canvas, frame4)
        toolbar.update()
        canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)



app = rngKit()
ani = animation.FuncAnimation(f, animate, interval=1000)
app.mainloop()
