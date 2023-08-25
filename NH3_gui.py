from guizero import App, Text, TextBox, Combo, PushButton, Box

selected_sensor1 = None
selected_sensor2 = None
lst_selected_sensor = [0, 0, 0, 0, 0, 0, 0, 0]
lst_sensor_color = ["gray",
                    "gray",
                    "gray",
                    "gray",
                    "gray",
                    "gray",
                    "gray",
                    "gray"]


def update_sensor_colors():
    # update the colors on the sensor buttons
    global lst_sensor_color
    btn_sensor0.bg = lst_sensor_color[0]
    btn_sensor1.bg = lst_sensor_color[1]
    btn_sensor2.bg = lst_sensor_color[2]
    btn_sensor3.bg = lst_sensor_color[3]
    btn_sensor4.bg = lst_sensor_color[4]
    btn_sensor5.bg = lst_sensor_color[5]
    btn_sensor6.bg = lst_sensor_color[6]
    btn_sensor7.bg = lst_sensor_color[7]

def do_nothing(button_number):
    global lst_sensor_color
    global lst_selected_sensor
    i = 0
    for sensor in lst_selected_sensor:
        if sensor == 1:
            print(f"Testing sensor {i}")
            lst_sensor_color[i] = "blue"

        i = i + 1
    print(f"button {button_number} pressed")
    update_sensor_colors()


def select_sensor(button_number):
    """ This Function will allow up to two sensor buttons to be selected at a time"""
    global lst_selected_sensor
    global lst_sensor_color

    # Toggle the selected sensor with the selected sensor button, unless two are already selected
    # Take into consideration the previous test

    if lst_selected_sensor[button_number] == 1:
        lst_selected_sensor[button_number] = 0
        lst_sensor_color[button_number] = "gray"
    elif sum(lst_selected_sensor) < (2 + lst_sensor_color.count("blue")):
        lst_selected_sensor[button_number] = 1
        lst_sensor_color[button_number] = "yellow"
    update_sensor_colors()

app = App(layout="grid", width=600, height=300)
lbl_item_num = Text(app, grid=[1, 0], text="Item Number:", align="right")
cmb_item_num = Combo(app, grid=[2, 0], options=["110280", "110281", "113930"], align="left")
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
lbl_status = Text(app, grid=[1, 5], text="Status:")
txt_status = TextBox(app, grid=[1, 6, 5, 1], text="", width=65)
btn_start = PushButton(app, grid=[2, 7], command=do_nothing, args=["Start"], text="Start")
btn_complete = PushButton(app, grid=[4, 7], command=do_nothing, args=["Complete"], text="Complete")
app.display()
