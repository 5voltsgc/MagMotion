from guizero import App, Text, TextBox, Combo, PushButton, Box

def do_nothing(button_number):
    print(f"button {button_number} pressed")


app = App(layout="grid")
lbl_item_num = Text(app, grid=[1, 0], text="Item Number:")
cmb_item_num = Combo(app, grid=[2, 0], options=["110280", "110281", "113930"])
lbl_serial_num = Text(app, grid=[1, 1], text="Serial Number:")
txt_serial_num = TextBox(app, grid=[2, 1], text="")
btn_box = Box(app, grid=[1, 3, 5, 1], layout="grid")
btn_sensor0 = PushButton(btn_box, command=do_nothing, text="0", grid=[1, 0], args=[0])
btn_sensor0.text_size = 25
btn_sensor1 = PushButton(btn_box, command=do_nothing, text="1", grid=[2, 0], args=[1])
btn_sensor1.text_size = 25
btn_sensor2 = PushButton(btn_box, command=do_nothing, text="2", grid=[3, 0], args=[2])
btn_sensor2.text_size = 25
btn_sensor3 = PushButton(btn_box, command=do_nothing, text="3", grid=[4, 0], args=[3])
btn_sensor3.text_size = 25
btn_sensor4 = PushButton(btn_box, command=do_nothing, text="4", grid=[5, 0], args=[4])
btn_sensor4.text_size = 25


app.display()
