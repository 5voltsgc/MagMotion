from guizero import App, Text, TextBox, Combo, PushButton, Box

selected_sensor1 = None
selected_sensor2 = None
num_sensors = 8

item_number_parm = [['110280', 'ASSY, CABLE, SENSOR, MFL, NH3, GEN 4, 6"', 5],
                    ['110281', 'ASSY, CABLE, SENSOR, MFL, NH3, GEN 4, 8"-10"', 4],
                    ]

item_number = [row[0] for row in item_number_parm]

def selected_item():
    global num_sensors
    global item_number

    # Find the selected item number from the drop down list
    selected = cmb_item_num.value
    # find row number or index (idx) representing the selected sensor item number
    idx = item_number.index(selected)
    # find the Number Sensors based on the selected sensor
    item_number = item_number_parm[idx][1]
    num_sensors = item_number_parm[idx][2]
    txt_status.value = f"Selected {item_number}, which has {num_sensors} sensors"


# list for keeping track of sensor under test
# 0=Sensor Number (same as index), 1=Tested, 2=selected to be tested, 3=color of button
lst_sensor_uut = [[0, 0, 0, "gray"],
                  [1, 0, 0, "gray"],
                  [2, 0, 0, "gray"],
                  [3, 0, 0, "gray"],
                  [4, 0, 0, "gray"],
                  [5, 0, 0, "gray"],
                  [6, 0, 0, "gray"],
                  [7, 0, 0, "gray"],
                  ]

def update_sensor_colors():
    # update the colors on the sensor buttons
    global lst_sensor_uut

    btn_sensor0.bg = lst_sensor_uut[0][3]
    btn_sensor1.bg = lst_sensor_uut[1][3]
    btn_sensor2.bg = lst_sensor_uut[2][3]
    btn_sensor3.bg = lst_sensor_uut[3][3]
    btn_sensor4.bg = lst_sensor_uut[4][3]
    btn_sensor5.bg = lst_sensor_uut[5][3]
    btn_sensor6.bg = lst_sensor_uut[6][3]
    btn_sensor7.bg = lst_sensor_uut[7][3]

def num_to_be_tested():
    total = 0
    for sensor in lst_sensor_uut:
        total = total + sensor[2]
    return total

def conduct_test(button_number):
    global lst_sensor_uut

    i = 0
    for sensor in lst_sensor_uut:
        if sensor[2] == 1:
            txt_status.value = (f"Testing sensor {i}")
            lst_sensor_uut[i][3] = "blue"
            lst_sensor_uut[i][2] = 0
            lst_sensor_uut[i][1] = 1
        i = i + 1

    print(f"button {button_number} pressed")
    update_sensor_colors()

def select_sensor(button_number):
    """ This Function will allow up to two sensor buttons to be selected at a time"""
    global lst_sensor_uut

    #  is this button already selected? if so deselect.
    if lst_sensor_uut[button_number][2] == 1:
        lst_sensor_uut[button_number][2] = 0
        lst_sensor_uut[button_number][3] = "gray"
    # count how many are selected if less than 2, add to be tested
    if num_to_be_tested() < 2:
        lst_sensor_uut[button_number][2] = 1
        lst_sensor_uut[button_number][3] = "yellow"

    update_sensor_colors()

    # if lst_sensor_uut[button_number][2] == 1:
    #     lst_sensor_uut[button_number] = 0
    #     lst_sensor_uut[button_number][3] = "gray"
    # elif sum(lst_selected_sensor) < (2 + lst_sensor_color.count("blue")):
    #     lst_sensor_uut[button_number] = 1
    #     lst_sensor_uut[button_number][3] = "yellow"

    # Toggle the selected sensor with the selected sensor button, unless two are already selected
    # Take into consideration the previous test

def do_nothing(button):
    print(f"the {button} was pressed")

def save_reset():
    # This function will save the collected data and save it out as a Excel Document
    # then reset the buttons by updating the lst_sensor_uut parameters
    reponse = app.yesno("info", "Do you want to save this test and reset?")
    if reponse:
        for sensor in lst_sensor_uut:
            sensor[1] = 0  # set all the tested (column 1) to 0
            sensor[2] = 0  # set all the selected (column 2) to 0
            sensor[3] = "gray"  # set all the colors (column 3) to "Gray"
    update_sensor_colors()
    # TODO save numpy array to excel
    # https://saturncloud.io/blog/dumping-numpy-arrays-into-an-excel-file-a-comprehensive-guide-for-data-scientists/

app = App(layout="grid", width=700, height=600)
lbl_item_num = Text(app, grid=[1, 0], text="Item Number:", align="right")
cmb_item_num = Combo(app, grid=[2, 0], options=[item_number], align="left", command=select_sensor)
lbl_serial_num = Text(app, grid=[1, 1], text="Serial Number:", align="right")
txt_serial_num = TextBox(app, grid=[2, 1], text="", align="left")
txt_sensors = Text(app, grid=[2, 3], text="Select up to two sensors to be tested")
btn_box = Box(app, grid=[1, 4, 5, 1], layout="grid", border=1)
btn_sensor0 = PushButton(btn_box, command=select_sensor, text="0", grid=[1, 0], args=[0])
btn_sensor0.text_size = 25
btn_sensor0.bg = "gray"
btn_sensor1 = PushButton(btn_box, command=select_sensor, text="1", grid=[2, 0], args=[1])
btn_sensor1.text_size = 25
btn_sensor1.bg = "gray"
btn_sensor2 = PushButton(btn_box, command=select_sensor, text="2", grid=[3, 0], args=[2])
btn_sensor2.text_size = 25
btn_sensor2.bg = "gray"
btn_sensor3 = PushButton(btn_box, command=select_sensor, text="3", grid=[4, 0], args=[3])
btn_sensor3.text_size = 25
btn_sensor3.bg = "gray"
btn_sensor4 = PushButton(btn_box, command=select_sensor, text="4", grid=[5, 0], args=[4])
btn_sensor4.text_size = 25
btn_sensor4.bg = "gray"
btn_sensor5 = PushButton(btn_box, command=select_sensor, text="5", grid=[6, 0], args=[5])
btn_sensor5.text_size = 25
btn_sensor5.bg = "gray"
btn_sensor6 = PushButton(btn_box, command=select_sensor, text="6", grid=[7, 0], args=[6])
btn_sensor6.text_size = 25
btn_sensor6.bg = "gray"
btn_sensor7 = PushButton(btn_box, command=select_sensor, text="7", grid=[8, 0], args=[7])
btn_sensor7.text_size = 25
btn_sensor7.bg = "gray"
txt_tip1 = Text(btn_box, grid=[0, 1, 8, 1], text="Gray: Not tested", align="left")
txt_tip2 = Text(btn_box, grid=[0, 2, 8, 1], text="Yellow: Selected for testing, max 2, at a time", align="left")
txt_tip1 = Text(btn_box, grid=[0, 3, 8, 1], text="Blue: Tested", align="left")
lbl_status = Text(app, grid=[1, 5], text="Status:", align="left")
txt_status = Text(app, grid=[1, 6, 5, 3], text="", width="fill", align="left")
btn_start = PushButton(app, grid=[2, 9], command=conduct_test, args=["Start"], text="Start")
btn_complete = PushButton(app, grid=[5, 9], command=save_reset, text="Complete")
app.display()
