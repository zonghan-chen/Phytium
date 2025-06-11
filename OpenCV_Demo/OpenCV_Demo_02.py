import cv2

img = cv2.imread("test.png")

if img is not None:
    print("图像读取成功！")

    cv2.namedWindow("Image", cv2.WINDOW_NORMAL)
    cv2.imshow("Image", img)

    print(f"图像尺寸：{img.shape}")
    print(f"图像数据类型：{img.dtype}")

    cv2.waitKey(0)
    cv2.destroyAllWindows()
else:
    print("图像读取失败！", flush=True)
