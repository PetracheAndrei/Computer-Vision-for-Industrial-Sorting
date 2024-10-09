from robodk import robolink    # RoboDK API
from robodk import robomath    # Robot toolbox
RDK = robolink.Robolink()

import random
import math
import cv2 as cv
import numpy as np
import os

# Initialize the RoboDK API
RDK = robolink.Robolink()

# List of object names
battery_names_list = [
    'AA(Duracell)', 'AA(Energizer)', 'AA(Lorem Ipsum)',
    'AAA(Duracell)', 'AAA(Energizer)', 'AAA(Lorem Ipsum)',
    'C(Duracell)', 'C(Energizer)', 'C(Lorem Ipsum)',
    'D(Duracell)', 'D(Energizer)', 'D(Lorem Ipsum)'
]
battery_sizes= [
    (0, 'AA', 52.5, 16.5),
    (1, 'AAA', 46.5, 12.5),
    (2, 'C', 52, 28.2),
    (3, 'D', 63.5, 36.2)
]
battery_types= [
    (0, 'Duracell'),
    (1, 'Energizer'),
    (2, 'Lorem Ipsum')
]
spaws_limits = [
    [(495, 540), (35, 75)],
    [(495, 540), (-75, -35)],
    [(390, 435), (35, 75)],
    [(390, 435), (-75, -35)]
]
# Dictionary to store the original objects and their copies
battery = {}
copy = {}

CAM_SIZE = 640, 480
MM_2_PIX = 340/220

CAM_NAME = 'My Camera'
CAM_PARAMS = f'SIZE={CAM_SIZE[0]}x{CAM_SIZE[1]}'
WINDOW_NAME = 'My Camera Feed'

# Get the camera item
cam_item = RDK.Item(CAM_NAME, robolink.ITEM_TYPE_CAMERA)
if not cam_item.Valid():
    cam_item = RDK.Cam2D_Add(RDK.AddFrame(CAM_NAME + ' Frame'), CAM_PARAMS)
    cam_item.setName(CAM_NAME)
cam_item.setParam('Open', 1)

screenshotCount = 2501
table_origin = 575, 110
box_data = {}
# Retrieve objects by name and store them in the dictionary
for name in battery_names_list:
    obj = RDK.Item(name, robolink.ITEM_TYPE_OBJECT)
    if obj.Valid():
        battery[name] = obj
    else:
        print(f"{name} not found!")

# Check if any valid objects were found
if not battery:
    print("No valid objects found!")

def boxSize(angle, x, y, width, height):
    width *= MM_2_PIX
    height *= MM_2_PIX
    theta = angle
    deg_angle = math.degrees(angle)
    cos_theta = math.cos(theta)
    sin_theta = math.sin(theta)

    # Calculate the coordinates of the corners of the rotated rectangle
    x_min = x - width / 2
    y_min = y - height / 2
    x_max = x + width / 2
    y_max = y + height / 2

    corner = [[0, 0] for _ in range(4)]
    corner[0][0] = x + cos_theta * (x_min - x) - sin_theta * (y_min - y)
    corner[0][1] = y + sin_theta * (x_min - x) + cos_theta * (y_min - y)

    corner[2][0] = x + cos_theta * (x_max - x) - sin_theta * (y_max - y)
    corner[2][1] = y + sin_theta * (x_max - x) + cos_theta * (y_max - y)

    corner[1][0] = x + cos_theta * (x_min - x) - sin_theta * (y_max- y)
    corner[1][1] = y + sin_theta * (x_min - x) + cos_theta * (y_max - y)

    corner[3][0] = x + cos_theta * (x_max - x) - sin_theta * (y_min - y)
    corner[3][1] = y + sin_theta * (x_max - x) + cos_theta * (y_min - y)

    all_x = [c[0] for c in corner]
    all_y = [c[1] for c in corner]

    x_min = min(all_x)
    y_min = min(all_y)
    x_max = max(all_x)
    y_max = max(all_y)

    new_height = x_max - x_min
    new_width = y_max - y_min

    return new_width, new_height
    
def convertYolo(image_width, image_height, x, y, boxW, boxH):
    x_center = x/image_width
    y_center = y/image_height
    box_width = boxW/image_width
    box_height = boxH/image_height
    
    return (x_center, y_center, box_width, box_height)
def createLabel(type, x, y, boxW, boxH):
    # Specify the file name
    filename = f"D:/L I C E N T A/Simulare/Training Images/Data/Brand/Labels/ImgToTrain_{screenshotCount+1}.txt"
    if os.path.exists(filename):
        # Read the file and count the number of rows
        with open(filename, 'r') as file:
            lines = file.readlines()
        
        if len(lines) >= 4:
            # If there are 4 or more rows, replace the content
            mode = 'w'
        else:
            # If there are fewer than 4 rows, append to the content
            mode = 'a'
    else:
        # If the file doesn't exist, create it and write to it
        mode = 'w'
    
    # Open the file in the determined mode
    with open(filename, mode) as file:
        file.write(f"{type} {round(x, 5)} {round(y, 5)} {round(boxW, 5)} {round(boxH, 5)}" + '\n')
def spawnNewBatteries(img):
    global battery
    global copy
    global box
    for i in range(4):
        random_battery = random.choice(list(battery.keys()))
        battery[random_battery].Copy()
        copy[i] = RDK.Paste()

        random_pose = battery[random_battery].PoseAbs()

        random_x = random.uniform(spaws_limits[i][0][0], spaws_limits[i][0][1]) 
        random_y = random.uniform(spaws_limits[i][1][0], spaws_limits[i][1][1])
        random_angle_y = math.radians(random.uniform(0, 360))  # Random angle around Y axis
        random_angle_z = math.radians(random.uniform(0, 360))  # Random angle around Z axis
        transl_matrix = robomath.transl(random_x, random_y, random_pose[2, 3]) * robomath.rotz(random_angle_z) * robomath.roty(random_angle_y)
        
        copy[i].setPoseAbs(transl_matrix)
        copy[i].setName(copy[i].Name() + '_COPY')

        copy_size = copy[i].Name()[:copy[i].Name().find("(")]
        copy_type = copy[i].Name()[copy[i].Name().find("(")+1:copy[i].Name().find(")")]
        print(copy_type)

        #Reversed X and Y, the orientation of the robot is diferent
        boxY = (table_origin[0] - random_x) * MM_2_PIX
        boxX = (table_origin[1] - random_y) * MM_2_PIX

        for battery_data in battery_sizes:
            if battery_data[1] == copy_size:
                for battery_brand in battery_types:
                    if battery_brand[1] == copy_type:
                        _, _, h, w = battery_data
                        kind, _ = battery_brand
                        boxH, boxW = boxSize(random_angle_z, boxX, boxY, h, w)
                        yoloX, yoloY, yoloW, yoloH = convertYolo(340, 340, boxX, boxY, boxW, boxH)
                        createLabel(kind, yoloX, yoloY, yoloW, yoloH)

                        box_data[i] = (boxX, boxY, boxW, boxH)
                break

def deleteSpawnedBatteries():
    global copy
    for i in range(4):
        copy[i].Delete()

takePhoto = False
while cam_item.setParam('isOpen') == '1':
    #----------------------------------
    # Method 1: Get the camera image, by socket
    img_socket = None
    bytes_img = RDK.Cam2D_Snapshot('', cam_item)
    if isinstance(bytes_img, bytes) and bytes_img != b'':
        nparr = np.frombuffer(bytes_img, np.uint8)
        img_socket = cv.imdecode(nparr, cv.IMREAD_COLOR)
    if img_socket is None:
        break
    
    crop_img = img_socket[69:409, 150:490]
    cv.imshow("Cropped", crop_img)
    
    if screenshotCount<2502:
        
        if takePhoto:
            deleteSpawnedBatteries()
            box = box_data
            # for i in range(4):
            #     cv.circle(crop_img, [int(box[i][0]), int(box[i][1])], radius=1, color = (0, 0, 255), thickness=-1)
            #     cv.rectangle(crop_img, [int(box[i][0]-box[i][2]/2), int(box[i][1]-box[i][3]/2)], [int(box[i][0]+box[i][2]/2), int(box[i][1]+box[i][3]/2)], (0, 255, 0), 2)
        else:
            takePhoto = True
        cv.waitKey(500)

        spawnNewBatteries(crop_img)
        cv.waitKey(500)

        cv.imshow("Cropped", crop_img)
        cv.imwrite(f'D:/L I C E N T A/Simulare/Training Images/Data/Brand/Images/ImgToTrain_{screenshotCount}.jpg', crop_img)

        print(f'Image saves as: ImgToTrain_{screenshotCount}')
        screenshotCount += 1

    key = cv.waitKey(1)
    if key == 27:
        break  # User pressed ESC, exit
    if cv.getWindowProperty(WINDOW_NAME, cv.WND_PROP_VISIBLE) < 1 and cv.getWindowProperty('Cropped', cv.WND_PROP_VISIBLE) < 1 or screenshotCount == 2501:
        deleteSpawnedBatteries()
        break  # User killed the main window, exit

# Close the preview and the camera. Ensure you call cam_item.setParam('Open', 1) before reusing a camera!
cv.destroyAllWindows()
RDK.Cam2D_Close(cam_item)
