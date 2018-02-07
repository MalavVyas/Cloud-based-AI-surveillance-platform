from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer

import tensorflow as tf
import time

class Classifier():
	
    def __init__(self, imagePath, modelVersion):    
        # Performance monitoring
        start = time.time();
        
        # Version of model to use [tf_files-vX.X]
        self.modelVersion = modelVersion
        
        # Initialize image data to None
        self.image_data = None;
    
        # Load image into class variable
        # self.loadImage(imagePath);
        
        # Counter for logging purposes
        self.count = 0;
        
        # Use the model version directory
        tf_files_dir = "../Models/tf_files-v%s" % self.modelVersion

        # Loads label file, strips off carriage return
        self.label_lines = [line.rstrip() for line in tf.gfile.GFile(tf_files_dir + "/retrained_labels.txt")]

        # Unpersists graph from file
        with tf.gfile.FastGFile(tf_files_dir + "/retrained_graph.pb", 'rb') as f:
            self.graph_def = tf.GraphDef()
            self.graph_def.ParseFromString(f.read())
            self._ = tf.import_graph_def(self.graph_def, name='')

            with tf.Session() as self.sess:
        
                # Feed the image_data as input to the graph and get last prediction
                self.softmax_tensor = self.sess.graph.get_tensor_by_name('final_result:0')

                # Log loading time
                print("Loaded Model v" + str(self.modelVersion) + " in %.2f seconds!" % (time.time() - start));

            
    def loadImage(self, image_path):
        # read in the image_data
        self.image_data = tf.gfile.FastGFile(image_path, 'rb').read();
    
    def classifyCNN(self, image_data=None):
        
        # If no image data was supplied
        if (image_data == None):
            # And classifier hasn't loaded image
            if (self.image_data == None):
                print("No image loaded yet!")
                return
            # Load class image data
            image_data = self.image_data;
            
        # Get predictions from softmax tensor layer
        predictions = self.sess.run(self.softmax_tensor, {'DecodeJpeg/contents:0': image_data})

        # Sort to show labels of first prediction in order of confidence
        top_k = predictions[0].argsort()[-len(predictions[0]):][::-1]

        result = {};
        
        for node_id in top_k:
            human_string = self.label_lines[node_id]
            score = predictions[0][node_id]
            result[human_string] = int(score * 100);
            
        return result;
            
            
