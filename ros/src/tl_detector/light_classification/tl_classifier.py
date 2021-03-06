from styx_msgs.msg import TrafficLight
import numpy as np
import tensorflow as tf
import rospy

# Modified code from tensorflow object detection repo
# https://github.com/tensorflow/models/blob/master/research/object_detection/object_detection_tutorial.ipynb


class TLClassifier(object):
    def __init__(self, is_real):
        self.map_class_to_tl = {
            1: TrafficLight.GREEN,
            2: TrafficLight.YELLOW,
            3: TrafficLight.RED,
            4: TrafficLight.UNKNOWN
        }
        self.map_class_to_str = {
            1: "GREEN",
            2: "YELLOW",
            3: "RED",
            4: "UNKNOWN"
        }

        # Load a (frozen) Tensorflow model into memory.
        self.detection_graph = tf.Graph()
        with self.detection_graph.as_default():
            od_graph_def = tf.GraphDef()
            import os
            path1 = (os.getcwd())
            if is_real:
                path1 += '/light_classification/trained_models/real/frozen_inference_graph.pb'
            else:
                path1 += '/light_classification/trained_models/sim/frozen_inference_graph.pb'

            with tf.gfile.GFile(path1, 'rb') as fid:
                serialized_graph = fid.read()
                od_graph_def.ParseFromString(serialized_graph)
                tf.import_graph_def(od_graph_def, name='')

            self.session = tf.Session(graph=self.detection_graph)

        # Definite input and output Tensors for detection_graph
        self.image_tensor = self.detection_graph.get_tensor_by_name(
            'image_tensor:0')
        # Each box represents a part of the image where a particular object was detected.
        self.detection_boxes = self.detection_graph.get_tensor_by_name(
            'detection_boxes:0')
        # Each score represent how level of confidence for each of the objects.
        # Score is shown on the result image, together with the class label.
        self.detection_scores = self.detection_graph.get_tensor_by_name(
            'detection_scores:0')
        self.detection_classes = self.detection_graph.get_tensor_by_name(
            'detection_classes:0')
        self.num_detections = self.detection_graph.get_tensor_by_name(
            'num_detections:0')

        # rospy.loginfo("WOLOLOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO Initialized")

    def get_classification(self, image):
        """Determines the color of the traffic light in the image

        Args:
            image (cv::Mat): image containing the traffic light

        Returns:
            int: ID of traffic light color (specified in styx_msgs/TrafficLight)

        """
        # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
        image_np_expanded = np.expand_dims(image, axis=0)
        # Actual detection.
        with self.detection_graph.as_default():
            (boxes, scores, classes, num) = self.session.run(
                [self.detection_boxes, self.detection_scores,
                 self.detection_classes,
                 self.num_detections],
                feed_dict={self.image_tensor: image_np_expanded})

        scores = np.squeeze(scores)
        boxes = np.squeeze(boxes)
        classes = np.squeeze(classes).astype(np.int32)
        indice = np.argmax(scores)

        if scores[indice] >= 0.5:
            rospy.loginfo(
                "*TL State = " + str(classes[indice]) + " " +
                self.map_class_to_str[
                    int(classes[indice])])
            return self.map_class_to_tl[int(classes[indice])]

        return TrafficLight.UNKNOWN
