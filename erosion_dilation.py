import cv2
import numpy as np
from constant import C

#
# ВЫРЕЗАНИЕ Конкретного цвета из картинки
#

###############################################################################################################
# Remove everything of a specific color (with a color variation tolerance) from an image with Python
#   https://stackoverflow.com/questions/72062001/remove-everything-of-a-specific-color-with-a-color-variation-tolerance-from-an
#

# # Load image
# im = cv2.imread(f'{C.ASSET_DIR}/result/stereonorth_5_10_18_MSG2-thunder_gpt_2-202504082300.png')
#
# # Define lower and upper limits of our blue
# BlueMin = np.array([90,  200, 200],np.uint8)
# BlueMax = np.array([100, 255, 255],np.uint8)
#
# # Go to HSV colourspace and get mask of blue pixels
# HSV  = cv2.cvtColor(im,cv2.COLOR_BGR2HSV)
# mask = cv2.inRange(HSV, BlueMin, BlueMax)
#
# # Make all pixels in mask white
# im[mask>0] = [100,100,100]
# # im[mask>0] = [255,255,255]
# cv2.imwrite(f'{C.ASSET_DIR}/result/output.png', im)


##############################
# detecting blue in image
#   https://stackoverflow.com/questions/77601019/detecting-blue-in-image#answer-77602308
#

# img = cv2.imread(f'{C.ASSET_DIR}/result/stereonorth_5_10_18_MSG2-thunder_gpt_2-202504082300.png')
#
# resized_img = cv2.resize(img ,(img.shape[1]//2,img.shape[0]//2))
#
# # В два раза меньше!!!!!!!
# hsv_image = cv2.cvtColor(resized_img,cv2.COLOR_BGR2HSV)
# # hsv_image = cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
#
# low_blue = np.array([90,215,110])
#
# high_blue = np.array([150,255,190])
#
# blue_mask = cv2.inRange(hsv_image,low_blue,high_blue)
#
# blue = cv2.bitwise_and(resized_img,resized_img,mask=blue_mask)
#
# cv2.imwrite(f'{C.ASSET_DIR}/result/output.png', blue)
# # cv2.imwrite(f'{C.ASSET_DIR}/result/output.png', img)




# import cv2
# import numpy as np
# from constant import C

# img = cv2.imread(f'{C.ASSET_DIR}/result/stereonorth_5_10_18_MSG2-thunder_gpt_2_masked-202504082300.png')
# blurred_img = cv2.medianBlur(img, 7)
#
# kernel = np.ones((5,5),np.uint8)
# # kernel = np.ones(5,np.uint8)
# erosion = cv2.erode(blurred_img, kernel, iterations=2)
# output = cv2.dilate(erosion, kernel, iterations=2)
# cv2.imwrite(f'{C.ASSET_DIR}/result/output.png', output)


# import skimage as ski
#
# image = ski.io.imread(f'{C.ASSET_DIR}/result/stereonorth_5_10_18_MSG2-thunder_gpt_2_masked-202504082300.png')
# # cleaned = ski.morphology.remove_small_objects(image, min_size=1000)
# cleaned = ski.morphology.remove_small_holes(image, area_threshold=10)
# ski.io.imsave(f'{C.ASSET_DIR}/result/output.png', cleaned)


# import cv2
# import numpy as np

# input = cv2.imread(f'{C.ASSET_DIR}/result/stereonorth_5_10_18_MSG2-thunder_gpt_2_masked-202504082300.png')
# div = 20
# quantized = input // div * div + div // 2
# cv2.imwrite(f'{C.ASSET_DIR}/result/output.png', quantized)

# import cv2
# import numpy as np
#
# def kmeans_color_quantization(image, clusters=8, rounds=1):
#     h, w = image.shape[:2]
#     samples = np.zeros([h*w,3], dtype=np.float32)
#     count = 0
#
#     for x in range(h):
#         for y in range(w):
#             samples[count] = image[x][y]
#             count += 1
#
#     compactness, labels, centers = cv2.kmeans(samples,
#             clusters,
#             None,
#             (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10000, 0.0001),
#             rounds,
#             cv2.KMEANS_RANDOM_CENTERS)
#
#     centers = np.uint8(centers)
#     res = centers[labels.flatten()]
#     return res.reshape((image.shape))
#
# image = cv2.imread(f'{C.ASSET_DIR}/result/stereonorth_5_10_18_MSG2-thunder_gpt_2_masked-202504082300.png')
# result = kmeans_color_quantization(image, clusters=400)
# cv2.imwrite(f'{C.ASSET_DIR}/result/output.png', result)