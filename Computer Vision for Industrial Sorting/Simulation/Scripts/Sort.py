from robodk import robolink    # RoboDK API
from robodk import robomath    # Robot toolbox
RDK = robolink.Robolink()

from robodk import *      # RoboDK API
from robolink import *    # Robot toolbox
# Link to RoboDK
# RDK = Robolink()

import os
from ultralytics import YOLO
import cv2 as cv
import numpy as np

CAM_SIZE = 640, 480

CAM_NAME = 'My Camera'
CAM_PARAMS = f'SIZE={CAM_SIZE[0]}x{CAM_SIZE[1]}'
WINDOW_NAME = 'My Camera Feed'
PIX_2_MM = 220/340

robot = RDK.Item(r'Fanuc LR Mate 200iD')
if not robot.Valid():
    raise Exception('Robot not connected!')

tool = RDK.Item("Gripper", robolink.ITEM_TYPE_TOOL)
robot.setPoseFrame(robot.PoseFrame())
robot.setPoseTool(robot.PoseTool())
robot.setRounding(10)
robot.setSpeed(10) 

target_ref = robot.Pose()
pos_ref = target_ref.Pos()
abovePick_Z = 100
table_origin = 365, 110
offset = 10, 25

cam_item = RDK.Item(CAM_NAME, robolink.ITEM_TYPE_CAMERA)
if not cam_item.Valid():
    cam_item = RDK.Cam2D_Add(RDK.AddFrame(CAM_NAME + ' Frame'), CAM_PARAMS)
    cam_item.setName(CAM_NAME)
cam_item.setParam('Open', 1)

target_item = RDK.Item("Target Test", robolink.ITEM_TYPE_TARGET)
target_home = RDK.Item("Home", robolink.ITEM_TYPE_TARGET)
target_item.setPose(target_home.Pose())

target_AA = RDK.Item("Target_AA", robolink.ITEM_TYPE_TARGET)
target_AAA = RDK.Item("Target_AAA", robolink.ITEM_TYPE_TARGET)
target_C = RDK.Item("Target_C", robolink.ITEM_TYPE_TARGET)
target_D = RDK.Item("Target_D", robolink.ITEM_TYPE_TARGET)

target_AAin = RDK.Item("Target_AAin", robolink.ITEM_TYPE_TARGET)
target_AAAin = RDK.Item("Target_AAAin", robolink.ITEM_TYPE_TARGET)
target_Cin = RDK.Item("Target_Cin", robolink.ITEM_TYPE_TARGET)
target_Din = RDK.Item("Target_Din", robolink.ITEM_TYPE_TARGET)

targets_sort = [target_AA, target_AAA, target_C, target_D]
targets_sortIN = [target_AAin, target_AAAin, target_Cin, target_Din]

spawnBatteries = RDK.Item("SpawnObjects", robolink.ITEM_TYPE_PROGRAM_PYTHON)
deleteBatteries = RDK.Item("DeleteObjects", robolink.ITEM_TYPE_PROGRAM_PYTHON)

modelAI_path = "D:/L I C E N T A/Simulare/Scripts/YOLOv8_Model_Detection/generations/gen_5.pt"
modelAI = YOLO(modelAI_path)
threshold = 0.9

def convertCoordinates(x, y):
    new_x = table_origin[0] + x * PIX_2_MM + offset[0]
    new_y = table_origin[1] - y * PIX_2_MM - offset[1]
    return new_x, new_y

def getZ (class_id):
    battery_sizes = [
    ('AA', 16.5),
    ('AAA', 12.5),
    ('C', 28.2),
    ('D', 36.2)
    ]
    height = battery_sizes[class_id][1]
    return height

frame_placeHolder = np.zeros((100,100,3), dtype=np.uint8)
delayFrames = 60
frames = delayFrames
while cam_item.setParam('isOpen') == '1':
    img_socket = None
    bytes_img = RDK.Cam2D_Snapshot('', cam_item)
    if isinstance(bytes_img, bytes) and bytes_img != b'':
        nparr = np.frombuffer(bytes_img, np.uint8)
        img_socket = cv.imdecode(nparr, cv.IMREAD_COLOR)
    if img_socket is None:
        break

    frame_cut = img_socket[69:409, 150:490]
    frame = cv.rotate(frame_cut, cv.ROTATE_90_CLOCKWISE)

    scanResults = modelAI(frame, verbose=False)[0]
    
    robot_joints = robot.Joints()
    robot_position = robot.SolveFK(robot_joints)
    robot_config = robot.JointsConfig(robot_joints)

    for i, result in enumerate(scanResults.boxes.data.tolist()):
        x, y, w, h, score, class_id = result
        realX, realY = convertCoordinates(x, y)
        print(class_id ,realX, realY)
        target = (realX, realY, abovePick_Z)

        target_pose = target_item.PoseAbs()
        target_pose.setPos([realX, realY, abovePick_Z])
        target_item.setPoseAbs(target_pose)

        if score > threshold:
            cv.rectangle(frame, (int(x), int(y)), (int(w), int(h)), (0, 255, 0), 4)
            cv.putText(frame, scanResults.names[int(class_id)].upper(), (int(x), int(y - 10)), cv.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 1, cv.LINE_AA)
            cv.imshow(WINDOW_NAME, frame)
            robot.MoveL(target_item, blocking=True)
            cv.waitKey(1000)
            
            target_pose.setPos([realX, realY, getZ(int(class_id))])
            target_item.setPoseAbs(target_pose)
            robot.MoveL(target_item, blocking=True)
            tool.AttachClosest()
            cv.waitKey(1000)

            target_pose.setPos([realX, realY, abovePick_Z])
            target_item.setPoseAbs(target_pose)
            robot.MoveL(target_item, blocking=True)
            cv.waitKey(1000)

            currentTarget = targets_sort[int(class_id)]
            robot.MoveL(currentTarget, blocking=True)
            cv.waitKey(1000)

            currentTarget = targets_sortIN[int(class_id)]
            robot.MoveL(currentTarget, blocking=True)
            tool.DetachAll()
            cv.waitKey(1000)

            currentTarget = targets_sort[int(class_id)]
            robot.MoveL(currentTarget, blocking=True)
            cv.waitKey(1000)

            if i == len(scanResults.boxes.data.tolist())-1:
                deleteBatteries.RunProgram()
                spawnBatteries.RunProgram()
            cv.waitKey(3000)

            currentTarget = target_home
            robot.MoveL(currentTarget, blocking=True)
            cv.waitKey(1000)
    
    key = cv.waitKey(1)
    if key == 27:
        break  # User pressed ESC, exit
    if cv.getWindowProperty(WINDOW_NAME, cv.WND_PROP_VISIBLE) < 1 and cv.getWindowProperty('My Camera Feed', cv.WND_PROP_VISIBLE) < 1:
        break  # User killed the main window, exit

# Close the preview and the camera. Ensure you call cam_item.setParam('Open', 1) before reusing a camera!
cv.destroyAllWindows()
RDK.Cam2D_Close(cam_item)