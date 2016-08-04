from threading import Thread
from picamera import PiCamera

class GameSaver:

    def __init__(self, fps=90, resolution=(640,480)):
        self.camera = PiCamera()
        
        self.camera.resolution = resolution
        self.camera.framerate = fps
        self.filename = None
        self.record_thread = None

    def start_recording(self, filename):
        self.record_thread = Thread(target=self.camera.start_recording(filename))
        self.record_thread.start()

    def stop_recording(self):
        self.camera.stop_recording()
