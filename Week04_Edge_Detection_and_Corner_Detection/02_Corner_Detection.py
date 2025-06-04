import cv2
import numpy as np
import matplotlib.pyplot as plt


def match_features(image1_path, image2_path):
    image1 = cv2.imread(image1_path)
    image2 = cv2.imread(image2_path)

    gray_image1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
    gray_image2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)

    # 创建SIFT对象
    sift = cv2.SIFT_create()

    # 检测图像关键点并计算其描述符
    keypoints1, descriptors1 = sift.detectAndCompute(gray_image1, None)
    keypoints2, descriptors2 = sift.detectAndCompute(gray_image2, None)

    # 创建FLANN匹配器
    flann_index_kdtree = 1

    index_params = dict(algorithm=flann_index_kdtree, trees=5)
    search_params = dict(checks=50)

    flann = cv2.FlannBasedMatcher(index_params, search_params)

    # 进行特征匹配
    matches = flann.knnMatch(descriptors1, descriptors2, k=2)

    good_matches = []

    # 使用Lowe比率测试筛选优质匹配
    for m, n in matches:
        if m.distance < 0.6 * n.distance:
            good_matches.append(m)

    # 获取匹配点坐标
    src_pts = np.float32([keypoints1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
    dst_pts = np.float32([keypoints2[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)

    # 使用RANSAC参数计算单应性矩阵
    h_matrix, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 3.0)

    # 使用mask筛选优质匹配
    good_matches = [m for i, m in enumerate(good_matches) if mask[i]]

    filtered_matches = []

    # 使用几何约束筛选优质匹配
    for m in good_matches:
        pt1 = keypoints1[m.queryIdx].pt
        pt2 = keypoints2[m.trainIdx].pt

        # 计算匹配点之间的距离
        dist = np.sqrt((pt1[0] - pt2[0]) ** 2 + (pt1[1] - pt2[1]) ** 2)

        if dist < max(image1.shape[0], image1.shape[1]) * 0.5:
            filtered_matches.append(m)

    good_matches = filtered_matches

    output_image = cv2.drawMatches(image1, keypoints1, image2, keypoints2, good_matches, None,
                                   flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)

    plt.figure(figsize=(25, 20))
    plt.imshow(cv2.cvtColor(output_image, cv2.COLOR_BGR2RGB))
    plt.title('Corner Detection and Feature Matching Results')
    plt.axis('off')
    plt.savefig('02_Output_Image.png')


def main():
    image1_path = "02_Original_Image_01.png"
    image2_path = "02_Original_Image_02.png"

    match_features(image1_path, image2_path)


if __name__ == "__main__":
    main()
