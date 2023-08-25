# Simple GUI: Conduct functinal testing with the RUST board,
# Read data from serial port and append to text box
# write this data to a file
# Jeff Watts
# Ver 1.0:  Created gui screen

from datetime import datetime
from guizero import App, Text, Combo, TextBox, PushButton, ListBox, Box, CheckBox
import serial.tools.list_ports
import serial.serialutil
import csv
import threading
import numpy as np
from matplotlib import pyplot as plt


serialCOM = "COM6"

def is_not_blank(s):
    return bool(s and not s.isspace())

def selected_item():
    selected = cmbo_item_number.value
    idx = item_number.index(selected)
    # a = Number DAQs
    a_txt.value = item_number_parm[idx][1]
    # b = Number Groups
    b_txt.value = item_number_parm[idx][2]
    # c = Number Sensors
    c_txt.value = item_number_parm[idx][3]
    # d = Test Type
    d_txt.value = item_number_parm[idx][4]
    # e = sample rate
    e_txt.value = item_number_parm[idx][5]
    extra = "0, 0, 0, 0, 0, 0"
    start_parms = f"<{a_txt.value}, {b_txt.value}, {c_txt.value}, {d_txt.value}, {e_txt.value}, {extra}>"
    txt_start_parameter.value = start_parms

def save_to_csv():
    print(f"save_to_csvwith file name: {txt_filename.value}")

def start_test():
    com_port = lst_ports.value
    now = datetime.now()  # current date and time
    date_time = now.strftime("%m_%d_%Y_%H_%M_%S")
    item_num = cmbo_item_number.value
    ser_num = txt_serial_Num.value
    filename = f"{item_num}_{ser_num}_{date_time}.csv"
    txt_filename.value = filename
    extra = "0, 0, 0, 0, 0, 0, 0"

    txt_status.append(txt_start_parameter.value)
    t1 = threading.Thread(target=data_collect)
    t1.start()
    t1.join

def data_collect():
    fileName = txt_filename.value
    f = open(fileName, "w")  # "w" to write over, "a" to append
    writer = csv.writer(f, lineterminator='\n')
    numSamples = int(a_txt.value)
    baudRate = 1000000
    serialCOM = lst_ports.value

    try:
        ser = serial.Serial(port=serialCOM, baudrate=baudRate, timeout=1)  # type: ignore
    except serial.serialutil.SerialException:
        txt_status.clear()
        txt_status.value = f"Serial port: {serialCOM}  not available!"
        txt_status.append("Please check, and try again")
        return None

    start_parms = txt_start_parameter.value
    ser.write(bytes(start_parms, 'utf-8'))
    rows = numSamples
    cols = int(b_txt.value) * int(c_txt.value)

    for i in range(numSamples):
        line = ser.readline()   # read a byte
        if line:
            string = line.decode()  # convert the byte string to a unicode string
            line = string.strip(", \n\r")

            txt_status.append(line)

            dataList = string.split(",")  # split the data by the added commas in Arduino File
            if (line != "BEGIN") and (line != "END"):
                dataList.pop()
            writer = csv.writer(f, lineterminator='\n')
            writer.writerow(dataList)
            # txt_status.append(dataList)

    f.close
    ser.close()
    print("---------------------------------------------------------------------------------------------")

def plot_chart(np_array):
    print("Chart")
    plt.plot(np_array)
    plt.show()


def find_available_ports():
    ports = serial.tools.list_ports.comports()
    com_list = []
    for p in ports:
        com_list.append(p.device)
    return com_list

def update_lst_ports():
    ports = serial.tools.list_ports.comports()
    lst_ports.clear()
    for p in ports:
        lst_ports.append(p.device)


def update_start_btn():
    serial_ready = is_not_blank(txt_serial_Num.value)
    ports_ready = is_not_blank(lst_ports.value)

    if serial_ready and ports_ready:
        btn_start.bg = 'green'
    else:
        btn_start.bg = 'gray'

def clear():
    txt_status.clear()


#  Header 0:Item Number, 1:DAQs, 2:Heads, 3:Halls/Head, 4:Test Type, 5:Sample Rate,
#           6: N/a, 7: N/a, 8: N/a, 9: N/a, 10: N/a, 11: N/a
item_number_parm = [['107287', '450', '4', '2', '2', '750', '0', '0', '0', '0', '0'],
                    ['107297', '450', '4', '2', '2', '750', '0', '0', '0', '0', '0'],
                    ['108144', '450', '4', '2', '2', '750', '0', '0', '0', '0', '0'],
                    ['108150', '450', '4', '2', '2', '750', '0', '0', '0', '0', '0'],
                    ['108283', '450', '3', '6', '1', '750', '0', '0', '0', '0', '0'],
                    ['108283', '450', '3', '6', '1', '750', '0', '0', '0', '0', '0'],
                    ['112497-01', '450', '4', '2', '2', '750', '0', '0', '0', '0', '0'],
                    ['121248', '450', '4', '3', '2', '750', '0', '0', '0', '0', '0'],
                    ['121249', '450', '4', '3', '3', '750', '0', '0', '0', '0', '0'],
                    ['121250', '450', '3', '6', '1', '750', '0', '0', '0', '0', '0'],
                    ['121334', '450', '3', '5', '1', '750', '0', '0', '0', '0', '0'],
                    ['121335', '450', '3', '5', '1', '750', '0', '0', '0', '0', '0'],
                    ['121791', '450', '2', '6', '1', '750', '0', '0', '0', '0', '0']
                    ]

# print(type(item_number_parm))
item_number = [row[0] for row in item_number_parm]
# print(item_number)
# print()
# print(item_number.index('121249'))
# print(item_number_parm[item_number.index('121249')][2])

avail_ports = find_available_ports()

app = App(layout="grid", width=1100, height=600, title="RUST")
app.repeat(100, update_start_btn)
box = Box(app, layout="grid", grid=[2, 0, 2, 4])
box.border = 1
a_lbl = Text(box, grid=[0, 0], text="DAQs: ", align='right')
a_txt = TextBox(box, text="450", grid=[1, 0])
b_lbl = Text(box, grid=[0, 1], text="# Groups: ", align='right')
b_txt = TextBox(box, text="3", grid=[1, 1])
c_lbl = Text(box, grid=[0, 2], text="# Sensors/Group: ", align='right')
c_txt = TextBox(box, text="6", grid=[1, 2])
d_lbl = Text(box, grid=[0, 3], text="Test Type: ", align='right')
d_txt = TextBox(box, text="1", grid=[1, 3],)
e_lbl = Text(box, grid=[0, 4], text="# Sample Rate: ", align='right')
e_txt = TextBox(box, text="750", grid=[1, 4])
f_chkb = CheckBox(box, text="Continous", grid=[2, 4])
f_chkb.text_size = 12

lbl_ItemNum = Text(app, grid=[0, 0], text="Item Number: ")
cmbo_item_number = Combo(app, options=item_number, grid=[1, 0], command=selected_item, align='left')
lbl_serial_number = Text(app, grid=[0, 1], text="Serial Number: ")
txt_serial_Num = TextBox(app, grid=[1, 1], align='left')
lbl_start_parameter = Text(app, grid=[0, 2], text="Start Parameters: ")
txt_start_parameter = TextBox(app, grid=[1, 2, 2, 1], text="", width=40, align='left')
lbl_ports = Text(app, grid=[0, 3], text="Comm Ports")
lst_ports = ListBox(app, grid=[1, 3], items=avail_ports, align='left', height=50, width=100)
btn_clear = PushButton(app, grid=[1, 9], text="Clear", command=clear)
btn_start = PushButton(app, grid=[2, 9], command=start_test, text="Start")
btn_start.bg = 'gray'
txt_status = TextBox(app, width=100, height=25, grid=[1, 4, 3, 2], multiline=True, scrollbar=True)
# txt_status.update_command(cursor_position_display)
# btn_save_csv = PushButton(app, grid=[4, 9], command=save_to_csv, text="Save to CSV")
txt_filename = TextBox(app, grid=[3, 9], width=40, text="Filename.csv")
app.display()
