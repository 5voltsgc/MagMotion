from guizero import App, Text, TextBox, Combo, PushButton, Box

selected_sensor1 = None
selected_sensor2 = None
lst_selected_sensor = [[0, 0, "gray"]
                       [1, 0, "gray"]
                       [2, 0, "gray"]
                       [3, 0, "gray"]
                       [4, 0, "gray"]
                       [5, 0, "gray"]
                       [6, 0, "gray"]
                       [7, 0, "gray"]]

def do_nothing(button_number):
    print(f"button {button_number} pressed")

def select_sensor(button_number):
    """ This Function will allow up to two sensor buttons to be selected at a time"""

    global selected_sensor1
    global selected_sensor2

    #  check to see if the selected sensor is already selected if so turn off
    if button_number == selected_sensor1:
        selected_sensor2 = None
    if button_number == selected_sensor2:
        selected_sensor2 = None

    # Move the selected_sensor2 to selected_sensor1 only if it is not None
    # and the newly selected sensor is put in selected_sensor2
    if selected_sensor2 is not None:
        selected_sensor1 = selected_sensor2
    else:  # is is None Newley selected sensor is move to selected_sensor1
        selected_sensor1 = button_number

    selected_sensor2 = button_number
    print(f"selected_sensor1 = {selected_sensor1}, and selected_sensor2 = {selected_sensor2}")

    # Update the button background to be selected
    if selected_sensor1 == 0 or selected_sensor2 == 0:
        btn_sensor0.bg = "yellow"
    else:
        btn_sensor0.bg = "gray"

    if selected_sensor1 == 1 or selected_sensor2 == 1:
        btn_sensor1.bg = "yellow"
    else:
        btn_sensor1.bg = "gray"

    if selected_sensor1 == 2 or selected_sensor2 == 2:
        btn_sensor2.bg = "yellow"
    else:
        btn_sensor2.bg = "gray"

    if selected_sensor1 == 3 or selected_sensor2 == 3:
        btn_sensor3.bg = "yellow"
    else:
        btn_sensor3.bg = "gray"

    if selected_sensor1 == 4 or selected_sensor2 == 4:
        btn_sensor4.bg = "yellow"
    else:
        btn_sensor4.bg = "gray"

    if selected_sensor1 == 5 or selected_sensor2 == 5:
        btn_sensor5.bg = "yellow"
    else:
        btn_sensor5.bg = "gray"

    if selected_sensor1 == 6 or selected_sensor2 == 6:
        btn_sensor6.bg = "yellow"
    else:
        btn_sensor6.bg = "gray"

    if selected_sensor1 == 7 or selected_sensor2 == 7:
        btn_sensor7.bg = "yellow"
    else:
        btn_sensor7.bg = "gray"

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
