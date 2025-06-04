import cv2
import argparse
import numpy as np


def show_image(image, edge_enhanced, edge_detection, output_path):
    # 调整图像大小
    height, width = image.shape[:2]

    margin = 10

    sub_width = width
    sub_height = height

    combined_width = sub_width * 3 + margin * 2
    combined_height = sub_height

    combined_image = np.ones((combined_height, combined_width, 3), dtype=np.uint8) * 255

    combined_image[0:sub_height, 0:sub_width] = image
    combined_image[0:sub_height, sub_width + margin:2 * sub_width + margin] = edge_enhanced
    combined_image[0:sub_height, 2 * sub_width + 2 * margin:3 * sub_width + 2 * margin] = edge_detection

    font = cv2.FONT_HERSHEY_SIMPLEX

    font_scale = 1
    font_color = (0, 0, 0)
    font_thickness = 2

    # 设置图像标题
    cv2.putText(combined_image, "Original", (10, 30), font, font_scale, font_color, font_thickness)
    cv2.putText(combined_image, "Edge Enhanced", (sub_width + margin + 10, 30), font, font_scale, font_color,
                font_thickness)
    cv2.putText(combined_image, "Edge Detection", (2 * sub_width + 2 * margin + 10, 30), font, font_scale, font_color,
                font_thickness)

    # 输出边缘检测结果
    cv2.imwrite(output_path, combined_image)
    print(f"结果已保存至: {output_path}")


def canny_edge_detection(input_path, output_path, low_threshold=100, high_threshold=200):
    image = cv2.imread(input_path)

    if image is None:
        raise ValueError(f"无法获取图片: {input_path}")

    # 将原图转化为灰度图
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # 使用高斯模糊进行降噪
    blurred_image = cv2.GaussianBlur(gray_image, (5, 5), 0)

    # 使用Canny算法进行边缘检测
    edges = cv2.Canny(blurred_image, low_threshold, high_threshold)

    # 创建边缘增强后的彩色图像
    colored_edges = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
    edge_enhanced = cv2.addWeighted(image, 0.7, colored_edges, 0.3, 0)

    # 创建图像边缘的黑白图像
    edge_detection = cv2.bitwise_not(edges)
    edge_detection = cv2.cvtColor(edge_detection, cv2.COLOR_GRAY2BGR)

    # 显示图像
    show_image(image, edge_enhanced, edge_detection, output_path)


def main():
    parser = argparse.ArgumentParser(description="Canny边缘检测")

    parser.add_argument('input', help='图片输入路径')
    parser.add_argument('output', help='图片输出路径')
    parser.add_argument('--low', type=int, default=100, help='Canny算法低阈值(默认值为100)')
    parser.add_argument('--high', type=int, default=200, help='Canny算法高阈值(默认值为200)')

    args = parser.parse_args()

    canny_edge_detection(args.input, args.output, args.low, args.high)


if __name__ == "__main__":
    main()
