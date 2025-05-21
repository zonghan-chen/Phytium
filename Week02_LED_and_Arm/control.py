import os
import time
from os import times

import serial
import threading
from arm_module import desktopArm

STATE_FILE_PATH = "state.txt"

BAUD_RATE = 115200
SERIAL_PORT = "/dev/ttyUSB0"
SERIAL_TIMEOUT = 0.1

targetPoints = [[150, -130], [150, -190], [150, -240], [-150, -130], [-150, -190], [-150, -240]]
height = 150

ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=SERIAL_TIMEOUT)
arm = desktopArm()

movement_lock = threading.RLock()
movement_thread = None

interrupt_event = threading.Event()

current_mode = "BLUE"


def save_state(state):
    with open(STATE_FILE_PATH, 'w') as f:
        f.write(state)


def load_state():
    if not os.path.exists(STATE_FILE_PATH):
        return "done"

    with open(STATE_FILE_PATH, 'r') as f:
        return f.read().strip()


def send_command_to_serial(command_str):
    global current_mode

    command = command_str + '\n'
    ser.write(command.encode())
    ser.flush()

    current_mode = command_str

    if command_str == "RED_ON":
        interrupt_event.set()
    else:
        interrupt_event.clear()


def stop_and_reset_arm():
    with movement_lock:
        arm.reset_position(times=2000)


def move_along_the_path():
    with movement_lock:
        for i, pos in enumerate(targetPoints):
            if interrupt_event.is_set():
                print("红灯亮！机械臂禁止运动并复位！")
                stop_and_reset_arm()
                return

            arm.move_point(x=pos[0], y=pos[1], z=height, times=2000)
            save_state(f"step_{i + 1}")

        arm.reset_position(times=2000)
        save_state("done")


def resume_arm_path():
    state = load_state()

    if state == "done":
        print("蓝灯亮！机械臂运动已完成无需恢复！")
        return

    idx = 0
    if state.startswith("step_"):
        idx = int(state.split('_')[1]) - 1

    if idx < 0:
        idx = 0

    with movement_lock:
        for i in range(idx, len(targetPoints)):
            if interrupt_event.is_set():
                print("红灯亮！机械臂禁止运动并复位！")
                stop_and_reset_arm()
                return

            arm.move_point(x=targetPoints[i][0], y=targetPoints[i][1], z=height, times=2000)
            save_state(f"step_{i + 1}")

        arm.reset_position(times=2000)
        save_state("done")


def launch_task(task):
    global movement_thread

    if movement_thread and movement_thread.is_alive():
        return

    movement_thread = threading.Thread(target=task)
    movement_thread.start()


if __name__ == "__main__":
    print("\n-------LED&机械臂控制程序-------")

    while True:
        print("\n命令列表：RED_ON / GREEN_ON / BLUE_ON / q")

        cmd = input("请输入命令：").strip().upper()

        if cmd == 'Q':
            print("退出LED&机械臂控制程序！")
            break
        elif cmd == "RED_ON":
            send_command_to_serial("RED_ON")
        elif cmd == "GREEN_ON":
            send_command_to_serial("GREEN_ON")
            launch_task(move_along_the_path)
        elif cmd == "BLUE_ON":
            send_command_to_serial("BLUE_ON")
            launch_task(resume_arm_path)
        else:
            print("无效命令！")

    ser.close()
