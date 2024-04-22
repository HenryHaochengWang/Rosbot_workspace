import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist
from tf2_ros import TransformListener, Buffer
from find_object_2d.msg import ObjectsStamped 


markers = {
    # 1: "start",
    7: "radioactive",
    11: "explosives",
    21: "flammable",
    22: "non-flammable gas",
    41: "dangous when wet",
    42: "combustible",
    43: "flammable solid",
    51: "oxidizer",
    52: "orgnic peroxide",
    61: "posion",
    62: "inhalation hazards"
}


class ImageLocalizer(Node):
    def __init__(self):
        super().__init__('image_localizer')
        self.subscription = self.create_subscription(
            ObjectsStamped, 
            '/objectsStamped', 
            self.object_callback, 
            10)
        self.publisher = self.create_publisher(Twist, 'cmd_vel', 10)
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)
        self.marked_objects = {}

    def object_callback(self, msg):
        id = -1
        if len(msg.objects.data) > 0:
            id = msg.objects.data[0]
            object_info = {
                'dx': msg.objects.data[9],
                'dy': msg.objects.data[10],
                'width': msg.objects.data[1],
                'height': msg.objects.data[2]
            }
        if self.object_available_to_mark(id):
            self.get_logger().info(f"New object detected: {id}")
            self.get_logger().info(f"Object position in image: ({object_info['dx']}, {object_info['dy']})")
            self.rotate_to_center_object(object_info)

    def object_available_to_mark(self, object_id):
        if id == -1:
            return False
        if not (object_id in self.marked_objects) and (object_id in markers):
            return True
        return False 

    def rotate_to_center_object(self, object):
        object_center_x = (object['dx'] + object['width']) / 2
        # Command robot to rotate so that the object is centered

        k = 0.005  
        error_x = 320 - object_center_x # 

        twist_msg = Twist()
        if abs(error_x) > 5:  
            # make sure speed is not too high and not too low, between 3 and 0.1
            twist_msg.angular.z = k * error_x
        else:
            twist_msg.angular.z = 0.0  

        self.publisher.publish(twist_msg)
        if twist_msg.angular.z == 0.0:
            self.align_complete = True
            # self.mark_object()
        else:
            self.align_complete = False

    def mark_object(self):
    #     TODO: Use laser sensor to detect the distence and tf to odom, then add marker into marked_objects
        pass


def main(args=None):
    rclpy.init(args=args)
    node = ImageLocalizer()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        rclpy.shutdown()
        print("Shutdown")


if __name__ == '__main__':
    main()
