import PySimpleGUI as sg
import matplotlib.pyplot as plt
from matplotlib import style
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import time
import threading

global thread
thread = False

def draw_figure(canvas, figure):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg

def increase(index_number_array, zscore_array):
    while thread:
        index_number_array.append(index_number_array[-1] + 1)
        zscore_array.append(zscore_array[-1] + 1)
        time.sleep(1)


def main():
    # define the form layout
    layout = [[sg.Text('Animated Matplotlib', size=(40, 1), justification='center', font='Helvetica 20')],
              [sg.Canvas(size=(640, 480), key='-CANVAS-')],
              [sg.Canvas(key='-CANVAS2-')],
              [sg.Button('Exit', size=(10, 2), pad=((280, 0), 3), font='Helvetica 14')],
              [sg.Button('Start', key="live_plot", size=(10, 2), pad=((280, 0), 3), font='Helvetica 14')]]

    # create the form and show it without the plot
    window = sg.Window('Demo Application - Embedding Matplotlib In PySimpleGUI', layout, finalize=True)

    canvas_elem = window['-CANVAS-']
    canvas2 = window['-CANVAS2-']
    canvas = canvas_elem.TKCanvas
    # draw the intitial plot
    style.use("ggplot")
    fig, ax = plt.subplots()
    fig_agg = draw_figure(canvas, fig)
    index_number_array = [1, 2, 3, 4]
    zscore_array = [3, 2, 1, 0]


    while True:
        event, values = window.read(timeout=10)
        if event in ("Exit", sg.WIN_CLOSED):  # always,  always give a way out!
            break
        elif event == 'live_plot':
            global thread
            if not thread:
                thread = True
                threading.Thread(target=increase, args=(index_number_array, zscore_array), daemon=True).start()
                window['live_plot'].update("Stop")
            else:
                thread = False
                window['live_plot'].update("Start")

        #ax.cla()
        #ax.clear()
        ax.plot(index_number_array, zscore_array, color='orange')
        ax.set_title("Live Plot")
        ax.set_xlabel('Time(s)', fontsize=10)
        ax.set_ylabel('Z-Score', fontsize='medium')
        fig_agg.draw()
    window.close()


if __name__ == '__main__':
    main()