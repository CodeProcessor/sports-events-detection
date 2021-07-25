'''
Created on 6/6/21

@author: dulanj
'''
import threading
import time
from queue import Queue

import cv2


class VideoReader():
    def __init__(self, filename: str):

        self.filename = filename
        self.cap = None
        self.init_capture()
        self.fps = 0
        self.frame_count = 0
        self.frame_queue = Queue(maxsize=5)
        self.clip_save_loc = "/home/dulanj/MSc/Research/data/clips"
        # super().__init__()

    def init_capture(self):
        self.cap = cv2.VideoCapture(self.filename)
        self.frame_count = 0

    def visualize(self):
        start_time = time.time()
        while True:
            ret, frame = self.cap.read()

            if ret:
                self.frame_count += 1
                cv2.imshow('display', frame)
                _key = cv2.waitKey(1)
                if self.frame_count % 10 == 0:
                    self.fps = self.frame_count / (time.time() - start_time)
                    print(f"FPS:{self.fps}")
                if _key == 27:
                    break

    def run(self) -> None:
        while True:
            if not self.frame_queue.full():
                ret, frame = self.cap.read()

                if ret:
                    self.frame_queue.put(frame)

    def read(self):
        return self.frame_queue.get()

    def grab_frame(self):
        self.cap.grab()
        self.frame_count += 1
        print(f"Grab: {self.frame_count}")

    def read_frame(self):
        ret, frame = self.cap.read()
        self.frame_count += 1
        return frame

    def seek(self, timestamp: int):
        if timestamp < self.frame_count:
            self.init_capture()

        while timestamp > self.frame_count:
            self.grab_frame()
        return 0

    def seek_n_read(self, timestamp: int):
        self.seek(timestamp)
        return self.read_frame()

    def __del__(self):
        self.cleanup()

    def save_clip(self, timestamp_from: int, timestamp_to: int) -> str:
        ...

    def cleanup(self):
        self.cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    file_path = "/home/dulanj/MSc/Research/CH & FC v Kandy SC - DRL 2019_20 Match #23.mp4"
    obj = VideoReader(file_path)
    obj.visualize()
