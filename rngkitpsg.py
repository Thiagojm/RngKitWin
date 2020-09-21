# Default imports
import time
import threading

# External imports
import pandas as pd
import PySimpleGUI as sg
import matplotlib.pyplot as plt
from matplotlib import style
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Internal imports
import rng_module as rm


global thread
thread = False

def live_plot(index_number_array, zscore_array):
    while thread:
        rm.increase(index_number_array, zscore_array)


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

    # TAB 1 - Captura/ Análise
    coluna_1_tab_1 = [[sg.Frame(title="Resumo", layout=[
        [sg.T("Ticker da ação:"), sg.Input(k="stock_name", size=(10, 1)),
         sg.B("Exibir", k="Exibir", bind_return_key=True)],
        [sg.T("Nome da Empresa:"), sg.T("", k="nome_empresa", size=(25, 1), relief="sunken")],
        [sg.T("Preço:", size=(27, 1)), sg.T("", k="preco_atual", size=(13, 1), relief="sunken")],
        [sg.T("Preço/Lucro(P/L):", size=(27, 1)), sg.T("", k="preco_lucro", size=(13, 1), relief="sunken")],
        [sg.T("Preço/Valor Patrimonial(P/VP):", size=(27, 1)), sg.T("", k="preco_vp", size=(13, 1), relief="sunken")],
        [sg.T("P/L * P/VP:", size=(27, 1)), sg.T("", k="pl_vp", size=(13, 1), relief="sunken")],
        [sg.T("Dividend Yield:", size=(27, 1)), sg.T("", k="div_yeild", size=(13, 1), relief="sunken")],
        [sg.T("Lucro por ação(LPA):", size=(27, 1)), sg.T("", k="LPA", size=(13, 1), relief="sunken")],
        [sg.T("Valor Patrimonial por ação(VPA):", size=(27, 1)), sg.T("", k="VPA", size=(13, 1), relief="sunken")],
        [sg.T("ROE:", size=(27, 1)), sg.T("", k="ROE", size=(13, 1), relief="sunken")],
        [sg.T("Liquidez Corrente:", size=(27, 1)), sg.T("", k="current_ratio", size=(13, 1), relief="sunken")],
        [sg.T("Dívida sobre Patrimômino:", size=(27, 1)), sg.T("", k="debt_to_equity", size=(13, 1), relief="sunken")],
        [sg.T("Lucro Líquido 12m:", size=(27, 1)), sg.T("", k="lucro_liquido_12m", size=(13, 1), relief="sunken")],
        [sg.T("Total de ações:", size=(27, 1)), sg.T("", k="total_shares", size=(13, 1), relief="sunken")]])]]

    coluna_2_tab_1 = [[sg.Frame(title="Índice PEG", layout=[
        [sg.T("PEG 12 meses:", size=(23, 1)), sg.T("", k="peg_12m", relief="sunken", size=(13, 1))],
        [sg.T("PEG 36 meses:", size=(23, 1)), sg.T("", k="peg_36m", relief="sunken", size=(13, 1))], ])],
                      [sg.Image(filename="datafiles/BitB.png")], [sg.Frame(title="Preço Justo da Ação", layout=[
            [sg.Text("Juros Brasil 10 anos:"), sg.Input(k="br_10_anos", size=(8, 1), default_text="6.5"),
             sg.B("Calcular", k="calcular")], [sg.T("Valor Intrínseco BR 10 anos:", size=(23, 1)),
                                               sg.T("", k="vi_10_anos", relief="sunken", size=(13, 1))]])]]

    tab1_layout = [[sg.Text("Rng Kit", relief="raised", justification="center", size=(70, 1), font=("Calibri, 24"))],
                   [sg.Column(coluna_1_tab_1), sg.Column(coluna_2_tab_1)]]

    # TAB 2 - Gráfico
    graph_options = [[sg.B("Start", k='live_plot')]]

    live_graph = [[sg.Canvas(key='-CANVAS-')]]


    tab2_layout = [[sg.Frame("Options", layout=graph_options, k="graph_options", size=(90, 9))],
                   [sg.Frame("Live Plot", layout=live_graph, k="graph", size=(90, 9))]]


    # TAB 3 - Instruções
    tab3_layout = [[sg.T("Instructions", relief="raised", justification="center", size=(70, 1), font=("Calibri, 24"))], [
        sg.Multiline(default_text="texto", size=(75, 19), disabled=True, enable_events=False, font=("Calibri, 20"),
                     pad=(5, 5))]]

    # LAYOUT
    layout = [[sg.TabGroup([[sg.Tab('Start', tab1_layout), sg.Tab('Live Plot', tab2_layout),
                             sg.Tab('Instructions', tab3_layout)]], tab_location="top",
                           font="Calibri, 18")]]

    # WINDOW
    window = sg.Window("RngKit ver 2.0.0 - by Thiago Jung", layout, size=(1024, 720), location=(50, 50),
                       finalize=True, element_justification="center", font="Calibri 18", resizable=True,
                       icon=("src/BitB.ico"))

    # Setting things up!
    canvas_elem = window['-CANVAS-']
    canvas = canvas_elem.TKCanvas
    # draw the intitial plot
    style.use("ggplot")
    fig, ax = plt.subplots(figsize=(10, 5), dpi=100)
    fig_agg = rm.draw_figure(canvas, fig)
    index_number_array = [1, 2, 3, 4]
    zscore_array = [3, 2, 1, 0]



    # LOOP
    while True:
        event, values = window.read(timeout=200)
        if event == sg.WIN_CLOSED:  # always,  always give a way out!
            break
        elif event == 'live_plot':
            global thread
            if not thread:
                thread = True
                threading.Thread(target=live_plot, args=(index_number_array, zscore_array), daemon=True).start()
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


if __name__ == '__main__':
    main()