import roslibpy
import base64
import numpy as np
import cv2
import time
import json

class ROS_Client:
    def __init__(self,host,port):
        """
        host: JetCobot ip
        port: Rosbridge WebSocket server port
        """

        self.client = roslibpy.Ros(host = host, port = port)
        self.client.run()

        if not self.client.is_connected:
            raise RuntimeError(f"Failed to connect to ROS at {self.host}:{self.port}")
        else:
            print("Connection was successful.")

        self.last_scene = None
        self.last_update_time = time.time()
        self.fps = 0

        self.pose = None

        self.scene_capturer = roslibpy.Topic(
            self.client,
            "SceneNode",
            "sensor_msgs/CompressedImage"
        )

        self.pose_receiver = roslibpy.Topic(
            self.client,
            "PoseNode",
            "std_msgs/String"
        )

        self.control_sender = roslibpy.Topic(
            self.client,
            'ControlNode',
            'std_msgs/String'
        )
        
        self.control_sender.advertise()

        def scene_capturer_callback(msg):
            """Internal callback for receiving images."""
            try:
                img_bytes = base64.b64decode(msg["data"])
                img_array = np.frombuffer(img_bytes, dtype=np.uint8)
                img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                if img is not None:
                    self.last_scene = img
                    self.fps = 1 / (time.time() - self.last_update_time)
                    self.last_update_time = time.time()
            except Exception as e:
                print("[RosImageClient] Callback error:", e)

        
        def pose_receiver_callback(msg):
            self.pose = json.loads(msg["data"])

        self.scene_capturer.subscribe(scene_capturer_callback)
        self.pose_receiver.subscribe(pose_receiver_callback)

        while self.pose is None:
            print("ROS_Client MSG: PoseNode don't get the bot Pose.")
            time.sleep(3)

        while self.last_scene is None:
            print("ROS_Client MSG: SceneNode don't get the bot scene.")
            time.sleep(3)

        print("ROS_Client MSG: All Nodes were ready")


    
    def control_angle(self, id, angle):
        data = json.dumps(
            {
                "tag":"Angle",
                "id":id,
                "angle":angle
            }
        )
        
        self.control_sender.publish(
            roslibpy.Message({"data":data})
        )
    
    def control_coord(self, id, coord):
        data = json.dumps(
            {
                "tag":"Coord",
                "id":id,
                "coord":coord
            }
        )

        self.control_sender.publish(
            roslibpy.Message({"data":data})
        )

    def control_angles(self, angles):
        data = json.dumps(
            {
                "tag":"Angles",
                "angle":angles
            }
        )
        
        self.control_sender.publish(
            roslibpy.Message({"data":data})
        )

    def control_coords(self, coords):
        data = json.dumps(
            {
                "tag":"Coords",
                "coord":coords
            }
        )
        
        self.control_sender.publish(
            roslibpy.Message({"data":data})
        )

    def control_gripper(self, grip_value):
        data = json.dumps(
            {
                "tag":"Gripper",
                "gripper":grip_value
            }
        )

        self.control_sender.publish(
            roslibpy.Message({"data":data})
        )

    def get_scene(self):
        return self.last_scene
    
    def get_angles(self):
        #print(self.pose["angle"])
        return self.pose["angle"]
    
    def get_coords(self):
        return self.pose["coord"]