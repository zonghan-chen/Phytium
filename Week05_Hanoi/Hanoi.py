import time
from arm_module import desktopArm

# 物块参数
BLOCK_THICKNESS = 13  # 物块厚度

# 机械臂移动参数
ARM_DOWN_OFFSET = 75  # 机械臂下降偏移量
ARM_PLACE_OFFSET = 3  # 机械臂放置偏移量
ARM_MOVE_HEIGHT = 220  # 机械臂移动巡航高度

# 汉诺塔参数
peg_state = {1: [], 2: [], 3: []}
peg_position = {1: (-75, -180), 2: (0, -180), 3: (75, -180)}

# 计数器
move_count = 0  # 搬运次数计数器

# 初始化机械臂
arm = desktopArm()
arm.reset_position(times=2000)


def move_block(from_peg, to_peg):
    global move_count

    from_state = peg_state[from_peg]
    to_state = peg_state[to_peg]

    block = from_state.pop()
    print(f"移动物块{block}: 柱{from_peg}-->柱{to_peg}")

    x1, y1 = peg_position[from_peg]
    x2, y2 = peg_position[to_peg]

    from_level = len(from_state)
    to_level = len(to_state)

    z1 = ARM_MOVE_HEIGHT - ARM_DOWN_OFFSET + from_level * BLOCK_THICKNESS
    z2 = ARM_MOVE_HEIGHT - ARM_DOWN_OFFSET + to_level * BLOCK_THICKNESS + ARM_PLACE_OFFSET

    # 抓取物块
    arm.move_point(x1, y1, ARM_MOVE_HEIGHT, times=2000)
    arm.move_point(x1, y1, z1, times=1000)
    arm.suck_up()
    time.sleep(0.5)
    arm.move_point(x1, y1, ARM_MOVE_HEIGHT, times=1000)

    # 放置物块
    arm.move_point(x2, y2, ARM_MOVE_HEIGHT, times=2000)
    arm.move_point(x2, y2, z2, times=1000)
    arm.suck_release()
    time.sleep(0.5)
    arm.move_point(x2, y2, ARM_MOVE_HEIGHT, times=1000)

    to_state.append(block)
    move_count += 1


def hanoi(n, start, aux, end):
    if n == 1:
        move_block(start, end)
    else:
        hanoi(n - 1, start, end, aux)
        move_block(start, end)
        hanoi(n - 1, aux, start, end)


def main():
    global move_count

    block_num_input = input("请输入物块总数: ")

    if not block_num_input.isdigit():
        print("ERROR: 请输入非负整数!")
        return

    block_num = int(block_num_input)

    peg_state[1] = list(range(block_num, 0, -1))
    print("初始状态: ", peg_state)

    # 重置计数器
    move_count = 0

    hanoi(block_num, 1, 2, 3)

    # 机械臂复位
    arm.reset_position(times=2000)

    print("完成状态: ", peg_state)
    print(f"搬运次数: {move_count}次")


if __name__ == "__main__":
    main()
