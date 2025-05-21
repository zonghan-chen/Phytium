import time
import serial
import threading

BAUD_RATE = 115200

SERIAL_PORT = '/dev/ttyUSB0'
SERIAL_TIMEOUT = 0.1

serial_connection = None
stop_reading_thread = False


def send_command_to_serial(ser, command_str):
    try:
        command = command_str + '\n'
        ser.write(command.encode('ascii'))
        print(f"发送命令成功：{command_str}")
    except Exception as e:
        print(f"发送命令错误：{e}")


def read_response_from_serial(ser):
    global stop_reading_thread

    buffer = b""

    while not stop_reading_thread:
        try:
            if ser and ser.is_open:
                if ser.in_waiting > 0:
                    data = ser.read(ser.in_waiting)

                    if data:
                        buffer += data

                        while b'\n' in buffer:
                            original_line, buffer = buffer.split(b'\n', 1)
                            original_line = original_line.rstrip(b'\r')

                            try:
                                decoded_line = original_line.decode('utf-8', errors='replace').strip()

                                if decoded_line:
                                    print(f"解码信息成功：{decoded_line}")
                            except Exception as de:
                                print(f"解码信息错误：{de}，原始信息：{original_line}")
                else:
                    time.sleep(0.01)
            else:
                if not stop_reading_thread:
                    print("串口未打开或已关闭！")
                    time.sleep(1)
        except serial.SerialException as se:
            if not stop_reading_thread:
                print(f"串口读取错误：{se}")
        except Exception as e:
            if not stop_reading_thread:
                print(f"未知错误：{e}")

    print("串口读取线程已停止！")


if __name__ == "__main__":
    try:
        serial_connection = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=SERIAL_TIMEOUT)
        print(f"串口 {SERIAL_PORT} 连接成功！")

        time.sleep(1)

        stop_reading_thread = False
        reading_thread = threading.Thread(target=read_response_from_serial, args=(serial_connection,))
        reading_thread.daemon = True
        reading_thread.start()

        time.sleep(1)

        print("\n-------LED控制程序-------")
        while True:
            print("\n命令列表：LED_ON / LED_OFF / LED_BREATH / q")

            cmd = input("请输入命令：").strip().upper()

            if cmd == 'Q':
                print("退出LED控制程序！")
                send_command_to_serial(serial_connection, "LED_OFF")
                break
            elif cmd in ["LED_ON", "LED_OFF", "LED_BREATH"]:
                send_command_to_serial(serial_connection, cmd)
            else:
                print("无效命令！")

            time.sleep(0.1)
    except serial.SerialException as se:
        print(f"串口连接错误：{se}")
    except KeyboardInterrupt:
        print("检测到Ctrl+C，退出LED控制程序！")

        if serial_connection and serial_connection.is_open:
            send_command_to_serial(serial_connection, "LED_OFF")
    except Exception as e:
        print(f"未知错误：{e}")
    finally:
        stop_reading_thread = True

        if 'reading_thread' in locals() and reading_thread.is_alive():
            reading_thread.join(timeout=1)

        if serial_connection and serial_connection.is_open:
            serial_connection.close()
