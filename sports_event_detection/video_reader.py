'''
Created on 6/6/21

@author: dulanj
'''
import time

import cv2


class VideoReader():
    def __init__(self, filename: str, verbose: bool = False):

        self.__filename = filename
        self.__cap = None

        self.__fps = 0
        self.__frame_shape = (0, 0)
        self.init_capture()
        self.__processing_fps = 0
        self.__frame_count = 0
        self.verbose = verbose
        self.read_fps_timestamp = 1
        # self.__frame_queue = Queue(maxsize=5)

        # super().__init__()

    def init_capture(self):
        self.__cap = cv2.VideoCapture(self.__filename)
        self.__frame_count = 0
        if self.__cap.isOpened():
            self.__fps = self.__cap.get(cv2.CAP_PROP_FPS)
            # get vcap property
            width = self.__cap.get(3)  # float `width`
            height = self.__cap.get(4)  # float `height`
            self.__frame_shape = (int(height), int(width))
            print("Video properties: ", self.__frame_shape, self.__fps)
        else:
            raise Exception("Video didnt open: {}".format(self.__filename))

    def get_fps(self) -> int:
        return int(self.__fps)

    def visualize(self):
        start_time = time.time()
        while True:
            ret, frame = self.__cap.read()

            if ret:
                self.__frame_count += 1
                cv2.imshow('display', frame)
                _key = cv2.waitKey(1)
                if self.__frame_count % 10 == 0:
                    fps = self.__frame_count / (time.time() - start_time)
                    print(f"FPS:{fps}")
                if _key == 27:
                    break

    def get_shape(self):
        return self.__frame_shape

    def __grab_frame(self):
        self.__cap.grab()
        self.__frame_count += 1
        if self.__frame_count % 1000 == 0:
            print(f"Grab: {self.__frame_count}")

    def read_frame(self):
        ret, frame = self.__cap.read()
        self.__frame_count += 1
        if self.verbose:
            interval = 100
            if self.__frame_count % interval == 0:
                print("Read FPS: ", interval / (time.time() - self.read_fps_timestamp))
                self.read_fps_timestamp = time.time()

        return frame if ret else None

    def get_video_time(self):
        seconds = self.__frame_count / self.get_fps()
        minutes = seconds // 60
        hours = minutes // 60
        seconds = seconds % 60
        minutes = minutes % 60
        return "{:02d}:{:02d}:{:02d}".format(int(hours), int(minutes), int(seconds))

    def seek(self, timestamp: int):
        if timestamp < self.__frame_count:
            self.init_capture()

        while timestamp > self.__frame_count:
            self.__grab_frame()
        print(f"Seek done: {self.__frame_count}")
        return 0

    def seek_n_read(self, timestamp: int):
        self.seek(timestamp)
        return self.read_frame()

    def __del__(self):
        self.cleanup()

    def save_clip(self, timestamp_from: int, timestamp_to: int) -> str:
        ...

    def cleanup(self):
        self.__cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    file_path = "/home/dulanj/MSc/DialogRugby/match-16.mp4"
    obj = VideoReader(file_path)
    obj.visualize()
