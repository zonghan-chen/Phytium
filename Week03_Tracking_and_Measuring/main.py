import sys
import cv2
import ctypes
import numpy as np

from PyQt5.QtCore import pyqtSignal, Qt, QTimer
from PyQt5.QtGui import QColor, QPainter, QImage, QPixmap
from PyQt5.QtWidgets import QFrame, QLabel, QMainWindow, QWidget, QHBoxLayout, QGroupBox, QVBoxLayout, QPushButton, \
    QDoubleSpinBox, QApplication

if sys.platform == 'win32':
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except(AttributeError, OSError):
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except(AttributeError, OSError):
            try:
                ctypes.windll.user32.SetProcessDPIAware()
            except(AttributeError, OSError):
                pass


class ColorBox(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(50, 50)
        self.setFrameShape(QFrame.Box)
        self.setFrameShadow(QFrame.Sunken)
        self.color = QColor(255, 0, 0)

    def set_color(self, color):
        self.color = color
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.fillRect(self.rect(), self.color)


class ClickableLabel(QLabel):
    clicked = pyqtSignal(int, int)

    def __init__(self, parent=None):
        super().__init__(parent)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            x = event.x()
            y = event.y()
            self.clicked.emit(x, y)


class VisionSystem(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("轨迹追踪&距离测量系统")
        self.setGeometry(100, 100, 1000, 800)

        self.cap = None
        self.camera_open = False

        self.camera_matrix = None
        self.dist_coeffs = None

        self.tracking = False
        self.measuring = False

        self.trajectory = []
        self.max_trajectory_points = 100

        self.focal_length = 1000
        self.known_width = 10.0

        self.color_picking = False
        self.current_frame = None

        self.lower_hsv = np.array([0, 100, 100])
        self.upper_hsv = np.array([10, 255, 255])
        self.lower_hsv2 = np.array([160, 100, 100])
        self.upper_hsv2 = np.array([180, 255, 255])
        self.use_two_ranges = True

        self.init_ui()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)

    def init_ui(self):
        # 主窗口（左侧控制面板+右侧视频流）
        main_widget = QWidget()
        main_layout = QHBoxLayout()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # 左侧控制面板
        control_panel = QGroupBox("控制面板")
        control_layout = QVBoxLayout()
        control_panel.setLayout(control_layout)
        control_panel.setFixedWidth(350)

        # 摄像头控制
        camera_group = QGroupBox("摄像头控制")
        camera_layout = QHBoxLayout()

        self.open_camera_button = QPushButton("打开摄像头")
        self.open_camera_button.clicked.connect(self.open_camera)

        self.close_camera_button = QPushButton("关闭摄像头")
        self.close_camera_button.clicked.connect(self.close_camera)
        self.close_camera_button.setEnabled(False)

        camera_layout.addWidget(self.open_camera_button)
        camera_layout.addWidget(self.close_camera_button)
        camera_group.setLayout(camera_layout)

        # 颜色选择器
        color_group = QGroupBox("颜色选择器")
        color_layout = QVBoxLayout()
        pick_color_layout = QHBoxLayout()

        self.pick_color_button = QPushButton("取色")
        self.pick_color_button.clicked.connect(self.toggle_color_picker)
        self.pick_color_button.setEnabled(False)
        pick_color_layout.addWidget(self.pick_color_button)

        self.color_display = ColorBox()
        pick_color_layout.addWidget(self.color_display)
        color_layout.addLayout(pick_color_layout)
        color_group.setLayout(color_layout)

        # 轨迹追踪
        exp1_group = QGroupBox("轨迹追踪")
        exp1_layout = QVBoxLayout()

        self.track_button = QPushButton("开始追踪")
        self.track_button.clicked.connect(self.toggle_tracking)
        self.track_button.setEnabled(False)

        self.clear_trajectory_button = QPushButton("清除轨迹")
        self.clear_trajectory_button.clicked.connect(self.clear_trajectory)
        self.clear_trajectory_button.setEnabled(False)

        exp1_layout.addWidget(self.track_button)
        exp1_layout.addWidget(self.clear_trajectory_button)
        exp1_group.setLayout(exp1_layout)

        # 距离测量
        exp2_group = QGroupBox("距离测量")
        exp2_layout = QVBoxLayout()

        self.calibrate_button = QPushButton("相机标定")
        self.calibrate_button.clicked.connect(self.calibrate_camera)
        self.calibrate_button.setEnabled(False)

        self.measure_button = QPushButton("开始测量")
        self.measure_button.clicked.connect(self.toggle_measuring)
        self.measure_button.setEnabled(False)

        # 已知物体宽度设置
        width_layout = QHBoxLayout()
        width_layout.addWidget(QLabel("已知物体宽度(cm): "))

        self.width_input = QDoubleSpinBox()
        self.width_input.setRange(0.1, 100.0)
        self.width_input.setValue(self.known_width)
        self.width_input.valueChanged.connect(self.update_known_width)
        width_layout.addWidget(self.width_input)

        # 相机标定状态显示
        self.calibration_status = QLabel("标定状态: 未标定")
        self.focal_length_label = QLabel("相机焦距: --")

        # 相机矩阵与畸变系数显示
        calib_params_group = QGroupBox("相机标定参数")
        calib_params_layout = QVBoxLayout()

        self.camera_matrix_label = QLabel("标定矩阵: ")
        self.camera_matrix_value = QLabel("未标定")

        self.dist_coeffs_label = QLabel("畸变系数: ")
        self.dist_coeffs_value = QLabel("未标定")

        calib_params_layout.addWidget(self.camera_matrix_label)
        calib_params_layout.addWidget(self.camera_matrix_value)
        calib_params_layout.addWidget(self.dist_coeffs_label)
        calib_params_layout.addWidget(self.dist_coeffs_value)
        calib_params_group.setLayout(calib_params_layout)

        exp2_layout.addWidget(self.calibrate_button)
        exp2_layout.addLayout(width_layout)
        exp2_layout.addWidget(self.calibration_status)
        exp2_layout.addWidget(self.focal_length_label)
        exp2_layout.addWidget(calib_params_group)
        exp2_layout.addWidget(self.measure_button)
        exp2_group.setLayout(exp2_layout)

        # 距离测量结果显示
        result_group = QGroupBox("测量结果")
        result_layout = QVBoxLayout()

        self.distance_label = QLabel("距离: --(cm)")
        self.position_label = QLabel("位置: (--, --)")

        result_layout.addWidget(self.distance_label)
        result_layout.addWidget(self.position_label)
        result_group.setLayout(result_layout)

        # 添加至控制面板
        control_layout.addWidget(camera_group)
        control_layout.addWidget(color_group)
        control_layout.addWidget(exp1_group)
        control_layout.addWidget(exp2_group)
        control_layout.addWidget(result_group)
        control_layout.addStretch()

        # 右侧视频流
        video_panel = QGroupBox("视频流")
        video_layout = QVBoxLayout()

        self.video_label = ClickableLabel()
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setMinimumSize(640, 480)
        self.video_label.clicked.connect(self.on_video_clicked)

        video_layout.addWidget(self.video_label)
        video_panel.setLayout(video_layout)

        # 添加至主窗口
        main_layout.addWidget(control_panel)
        main_layout.addWidget(video_panel)

    def open_camera(self):
        if not self.camera_open:
            self.cap = cv2.VideoCapture(0)

            if not self.cap.isOpened():
                print("无法打开摄像头")
                return

            self.camera_open = True
            self.timer.start(30)

            # 更新按钮状态
            self.open_camera_button.setEnabled(False)
            self.close_camera_button.setEnabled(True)
            self.pick_color_button.setEnabled(True)
            self.track_button.setEnabled(True)
            self.clear_trajectory_button.setEnabled(True)
            self.calibrate_button.setEnabled(True)
            self.measure_button.setEnabled(True)

            print("已打开摄像头")

    def close_camera(self):
        if self.camera_open:
            self.timer.stop()

            if self.cap is not None:
                self.cap.release()
                self.cap = None

            self.camera_open = False

            # 清空视频流显示
            self.video_label.clear()

            # 停止轨迹追踪、距离测量和取色
            self.tracking = False
            self.measuring = False
            self.color_picking = False
            self.track_button.setText("开始追踪")
            self.measure_button.setText("开始测量")
            self.pick_color_button.setText("取色")

            # 更新状态按钮
            self.open_camera_button.setEnabled(True)
            self.close_camera_button.setEnabled(False)
            self.pick_color_button.setEnabled(False)
            self.track_button.setEnabled(False)
            self.clear_trajectory_button.setEnabled(False)
            self.calibrate_button.setEnabled(False)
            self.measure_button.setEnabled(False)

            print("已关闭摄像头")

    def toggle_color_picker(self):
        self.color_picking = not self.color_picking

        if self.color_picking:
            self.pick_color_button.setText("取色中...")

            self.tracking = False
            self.measuring = False
            self.track_button.setText("开始追踪")
            self.measure_button.setText("开始测量")

            print("点击视频流取色")
        else:
            self.pick_color_button.setText("取色")

    def toggle_tracking(self):
        self.tracking = not self.tracking

        if self.tracking:
            self.measuring = False
            self.track_button.setText("停止追踪")
            self.measure_button.setText("开始测量")
        else:
            self.track_button.setText("开始追踪")

    def clear_trajectory(self):
        self.trajectory = []

    def calibrate_camera(self):
        print("请拍摄棋盘格以进行相机标定 (按Enter/Esc键退出)")

        chessboard_size = (9, 6)
        square_size = 2.40

        img_points = []
        obj_points = []

        objp = np.zeros((chessboard_size[0] * chessboard_size[1], 3), np.float32)
        objp[:, :2] = np.mgrid[0:chessboard_size[0], 0:chessboard_size[1]].T.reshape(-1, 2) * square_size

        # 创建标定窗口
        cv2.namedWindow("Calibration", cv2.WINDOW_NORMAL)
        cv2.moveWindow("Calibration", 20, 20)

        while True and self.camera_open:
            ret, frame = self.cap.read()

            if not ret:
                return

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            ret, corners = cv2.findChessboardCorners(gray, chessboard_size, None)

            if ret:
                img_points.append(corners)
                obj_points.append(objp)
                cv2.drawChessboardCorners(frame, chessboard_size, corners, ret)

            cv2.imshow("Calibration", frame)

            key = cv2.waitKey(1) & 0xFF
            if key == 13:
                break
            elif key == 27:
                break

        cv2.destroyWindow("Calibration")

        if img_points and obj_points:
            ret, self.camera_matrix, self.dist_coeffs, _, _ = cv2.calibrateCamera(obj_points, img_points,
                                                                                  gray.shape[::-1], None, None)

            print("相机标定成功")
            print("相机矩阵:\n", self.camera_matrix)
            print("畸变系数:\n", self.dist_coeffs)

            self.calibration_status.setText("标定状态: 已标定")

            if self.camera_matrix is not None:
                self.focal_length = (self.camera_matrix[0, 0] + self.camera_matrix[1, 1]) / 2
                self.focal_length_label.setText(f"相机焦距: {self.focal_length:.2f}")

                # 格式化显示相机矩阵
                matrix_text = ""

                for i in range(3):
                    row = " ".join([f"{self.camera_matrix[i, j]:.2f}" for j in range(3)])
                    matrix_text += f"[{row}]<br>"

                self.camera_matrix_value.setText(matrix_text)

                # 格式化显示畸变系数
                dist_text = "["

                for i in range(len(self.dist_coeffs[0])):
                    dist_text += f"{self.dist_coeffs[0][i]:.4f}"

                    if i < len(self.dist_coeffs[0]) - 1:
                        dist_text += ", "

                dist_text += "]"

                self.dist_coeffs_value.setText(dist_text)
        else:
            print("相机标定失败 (未检测到棋盘格角点)")

            self.calibration_status.setText("标定状态: 标定失败")
            self.camera_matrix_value.setText("标定失败")
            self.dist_coeffs_value.setText("标定失败")

    def toggle_measuring(self):
        self.measuring = not self.measuring

        if self.measuring:
            self.tracking = False
            self.track_button.setText("开始追踪")
            self.measure_button.setText("停止测量")
        else:
            self.measure_button.setText("开始测量")

    def update_known_width(self, value):
        self.known_width = value

    def on_video_clicked(self, x, y):
        if not self.color_picking or self.current_frame is None:
            return

        img_width = self.current_frame.shape[1]
        img_height = self.current_frame.shape[0]

        display_width = self.video_label.width()
        display_height = self.video_label.height()

        scale_x = img_width / display_width
        scale_y = img_height / display_height

        orig_x = int(x * scale_x)
        orig_y = int(y * scale_y)

        if 0 <= orig_x < img_width and 0 <= orig_y < img_height:
            b, g, r = self.current_frame[orig_y, orig_x]
            rgb_color = (r, g, b)

            qcolor = QColor(r, g, b)
            self.color_display.set_color(qcolor)

            pixel = np.uint8([[[b, g, r]]])
            hsv_pixel = cv2.cvtColor(pixel, cv2.COLOR_BGR2HSV)
            h, s, v = hsv_pixel[0][0]

            h_range = 15
            s_min = max(0, s - 50)
            s_max = min(255, s + 50)
            v_min = max(0, v - 50)
            v_max = min(255, v + 50)

            if h - h_range < 0 or h + h_range > 180:
                self.use_two_ranges = True

                self.lower_hsv = np.array([0, s_min, v_min])
                self.upper_hsv = np.array([h + h_range if h < h_range else h_range, s_max, v_max])
                self.lower_hsv2 = np.array([180 - h_range if h > 180 - h_range else h - h_range, s_min, v_min])
                self.upper_hsv2 = np.array([180, s_max, v_max])
            else:
                self.use_two_ranges = False

                self.lower_hsv = np.array([max(0, h - h_range), s_min, v_min])
                self.upper_hsv = np.array([min(180, h + h_range), s_max, v_max])

            self.color_picking = False
            self.pick_color_button.setText("取色")

            print(f"已选取颜色: RGB = {rgb_color}, HSV = ({h}, {s}, {v})")

    def update_frame(self):
        if not self.camera_open or self.cap is None:
            return

        ret, frame = self.cap.read()

        if not ret:
            return

        self.current_frame = frame.copy()

        # 使用相机标定参数校正图形
        if self.camera_matrix is not None and self.dist_coeffs is not None:
            h, w = frame.shape[:2]
            new_camera_matrix, roi = cv2.getOptimalNewCameraMatrix(self.camera_matrix, self.dist_coeffs, (w, h), 1,
                                                                   (w, h))
            frame = cv2.undistort(frame, self.camera_matrix, self.dist_coeffs, None, new_camera_matrix)

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # 检测物体颜色
        if self.use_two_ranges:
            mask1 = cv2.inRange(hsv, self.lower_hsv, self.upper_hsv)
            mask2 = cv2.inRange(hsv, self.lower_hsv2, self.upper_hsv2)
            color_mask = cv2.bitwise_or(mask1, mask2)
        else:
            color_mask = cv2.inRange(hsv, self.lower_hsv, self.upper_hsv)

        kernel = np.ones((5, 5), np.uint8)
        color_mask = cv2.morphologyEx(color_mask, cv2.MORPH_OPEN, kernel)
        color_mask = cv2.morphologyEx(color_mask, cv2.MORPH_CLOSE, kernel)

        # 确定物体轮廓
        contours, _ = cv2.findContours(color_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # 处理检测结果
        detected = False
        center = None
        radius = 0

        if len(contours) > 0:
            c = max(contours, key=cv2.contourArea)

            # 确定最小外接圆
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            center = (int(x), int(y))

            if radius > 10:
                detected = True

                # 绘制物体轮廓和中心点
                cv2.circle(frame, center, int(radius), (0, 255, 255), 2)
                cv2.circle(frame, center, 5, (0, 0, 255), -1)

                # 轨迹追踪
                if self.tracking:
                    self.trajectory.append(center)

                    if len(self.trajectory) > self.max_trajectory_points:
                        self.trajectory.pop(0)

                    # 绘制轨迹
                    for i in range(1, len(self.trajectory)):
                        cv2.line(frame, self.trajectory[i - 1], self.trajectory[i], (255, 0, 0), 2)

                # 距离测量
                if self.measuring and detected:
                    distance = (self.known_width * self.focal_length) / (2 * radius)

                    self.distance_label.setText(f"距离: {distance:.2f}(cm)")
                    self.position_label.setText(f"位置: ({center[0]}, {center[1]})")

                    cv2.putText(frame, f"{distance:.2f}(cm)", (center[0], center[1] - 20), cv2.FONT_HERSHEY_SIMPLEX,
                                0.5, (255, 255, 255), 2)

        if not detected and self.measuring:
            self.distance_label.setText("距离: --(cm)")
            self.position_label.setText("位置: (--, --)")

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 100, 200)
        edges_colored = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

        frame = cv2.addWeighted(frame, 0.8, edges_colored, 0.2, 0)

        display_frame = frame

        rgb_image = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image)

        self.video_label.setPixmap(
            pixmap.scaled(self.video_label.width(), self.video_label.height(), Qt.KeepAspectRatio))

    def closeEvent(self, event):
        if self.camera_open:
            self.close_camera()

        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = VisionSystem()
    window.show()

    sys.exit(app.exec_())
