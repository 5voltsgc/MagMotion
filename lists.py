
NUM_SENSORS = 8
lst_sensor_uut = [[0, 0, 0, "gray"],
                  [1, 0, 1, "gray"],
                  [2, 1, 0, "yellow"],
                  [3, 1, 1, "gray"],
                  [4, 1, 0, "gray"],
                  [5, 1, 0, "gray"],
                  [6, 0, 0, "gray"],
                  [7, 0, 0, "gray"],
                  ]
print(lst_sensor_uut[2][3])
j = 0

for i in range(NUM_SENSORS):
    j = j + lst_sensor_uut[i][2]
print(j)

total = 0
for sensor in lst_sensor_uut:
    total = total + sensor[2]
print(total)

    # if lst_selected_sensor[button_number] == 1:
    #     lst_selected_sensor[button_number] = 0
    #     lst_sensor_uut[button_number][3] = "gray"
    # elif sum(lst_selected_sensor) < (2 + lst_sensor_color.count("blue")):
    #     lst_selected_sensor[button_number] = 1
    #     lst_sensor_uut[button_number][3] = "yellow"
