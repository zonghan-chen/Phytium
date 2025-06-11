import numpy as np
import cv2


def display_image_properties(img):
    print(f"图像尺寸：{img.shape}")
    print(f"图像数据类型：{img.dtype}")
    print(f"图像通道数：{img.shape[2] if len(img.shape) > 2 else 1}")


def modify_image_properties(image_path):
    img = cv2.imread(image_path)

    if img is None:
        print("图像读取失败！")
        return

    print("原始图图像属性：")
    display_image_properties(img)

    # 显示原始图
    cv2.imshow("Original Image", img)
    cv2.waitKey(0)

    # 修改图像尺寸
    resized_img = cv2.resize(img, (200, 100))
    print("\nResize图图像属性：")
    display_image_properties(resized_img)

    # 修改图像数据类型
    float_img = img.astype(np.float32) / 255.0
    print("\nFloat32图图像属性：")
    display_image_properties(float_img)

    # 修改图像通道数（生成灰度图）
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    print("\n灰度图图像属性：")
    display_image_properties(gray_img)

    # 显示Resize图和灰度图
    cv2.imshow("Resized Image", resized_img)
    cv2.imshow("Grayscale Image", gray_img)

    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    image_path = "test.png"
    modify_image_properties(image_path)
