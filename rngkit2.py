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

f = Figure(figsize=(5, 5), dpi=100)
a = f.add_subplot(111)

# teste
index_number_array = [1, 2, 3, 4, 5]
zscore_array = [10, 20, 12, 13, 9]

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

        frame1 = tk.Frame(self, relief="raised", borderwidth=1)
        frame1.pack(fill="x")

        # Radiobuttons
        selectedLive = tk.IntVar()
        selectedLive.set(1)
        radBlive = tk.ttk.Radiobutton(frame1, text='Bitbabbler', value=1, variable=selectedLive)
        radBlive.pack(side=tk.TOP)
        selectedComboLive = tk.StringVar()
        comboBLive = ttk.Combobox(frame1, width=3)
        comboBLive['values'] = (0, 1)
        comboBLive.current(0)
        comboBLive.pack(side=tk.TOP)
        radTrngLive = tk.ttk.Radiobutton(frame1, text='TrueRng', value=2, variable=selectedLive)
        radTrngLive.pack()

        # Canvas
        canvas = FigureCanvasTkAgg(f, self)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        toolbar = NavigationToolbar2Tk(canvas, self)
        toolbar.update()
        canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

app = rngKit()
ani = animation.FuncAnimation(f, animate, interval=1000)
app.mainloop()
