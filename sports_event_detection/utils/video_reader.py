'''
Created on 6/6/21

@author: dulanj
'''
import logging
import os
import sys
import time

import cv2
from PIL import Image
from tqdm import tqdm


class VideoReader():
    def __init__(self, filename: str, verbose: bool = False):
        self.__filename = filename
        self.__cap = None
        self.pbar = None
        self.verbose = verbose

        self.__fps = 0
        self.__total_frame_count = 0
        self.__frame_shape = (0, 0)
        self.init_capture()
        self.__processing_fps = 0
        self.__frame_count = 0
        self.read_fps_timestamp = 1
        # self.__frame_queue = Queue(maxsize=5)

        # super().__init__()

    def get_video_info(self):
        print("FPS:", self.get_fps())
        print("Frame count:", self.get_total_frame_count())
        print("Frame size:", self.get_shape())

    def get_video_name(self):
        return os.path.splitext(os.path.basename(self.__filename))[0]

    def init_capture(self):
        self.__cap = cv2.VideoCapture(self.__filename)
        self.__frame_count = 0
        if self.__cap.isOpened():
            self.__fps = self.__cap.get(cv2.CAP_PROP_FPS)
            self.__total_frame_count = int(self.__cap.get(cv2.CAP_PROP_FRAME_COUNT))
            # get vcap property
            width = self.__cap.get(3)  # float `width`
            height = self.__cap.get(4)  # float `height`
            self.__frame_shape = (int(height), int(width))
            print(f"Video properties: {self.__frame_shape} {self.__fps} "
                  f"{self.__total_frame_count} | Name:  {os.path.basename(self.__filename)}")
        else:
            raise Exception("Video didnt open: {}".format(self.__filename))

    def set_progress_bar_limit(self, frame_count: int):
        if self.verbose:
            if self.pbar is not None:
                self.pbar.close()
            logging.info("Set progress bar limit: {}".format(frame_count))
            self.pbar = tqdm(total=frame_count, desc="Video Reader")
        else:
            logging.info("Nothing to do set, verbose is False")

    def get_fps(self) -> int:
        return self.__fps

    def get_total_frame_count(self):
        return self.__total_frame_count

    def get_video_duration(self):
        return self.get_video_time(self.__total_frame_count)

    def visualize(self, fps: int = None):
        start_time = time.time()
        _viz_fps_count = 100
        while True:
            ret, frame = self.__cap.read()

            if ret:
                self.__frame_count += 1
                cv2.imshow('display', frame)
                _key = cv2.waitKey(1)
                if self.__frame_count % _viz_fps_count == 0:
                    fps = _viz_fps_count / (time.time() - start_time)
                    start_time = time.time()
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

    def read_frame(self, pil_image=False):
        _is_frame, frame = self.__cap.read()
        self.__frame_count += 1
        if self.verbose:
            if self.pbar is None:
                self.pbar = tqdm(total=self.__total_frame_count, desc="Video Reader")
            self.pbar.update(1)
            interval = 100
            if self.__frame_count % interval == 0:
                _fps = interval / (time.time() - self.read_fps_timestamp)
                # print("Video Reader - Frame No: {}/{} Read FPS: {}".format(
                #     self.__frame_count, self.__total_frame_count, _fps)
                # )
                self.read_fps_timestamp = time.time()
                self.pbar.set_description(f"Processing at {_fps:.0f} FPS [{_fps / self.__fps:.0f}X]")
        ret = None
        if _is_frame:
            if pil_image:
                img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                ret = Image.fromarray(img)
            else:
                ret = frame
        return ret

    def get_video_time(self, frame_count=None):
        if frame_count is None:
            frame_count = self.__frame_count
        seconds = frame_count / self.get_fps()
        minutes = seconds // 60
        hours = minutes // 60
        seconds = seconds % 60
        minutes = minutes % 60
        return "{:02d}:{:02d}:{:02d}".format(int(hours), int(minutes), int(seconds))

    def get_frame_no(self, video_time_str=None):
        if video_time_str is None:
            frame_no = self.__frame_count
        else:
            try:
                video_time_str = video_time_str.replace(".", ":")
                _hh, _mm, _ss = video_time_str.split(":")
                seconds = int(_hh) * 3600 + int(_mm) * 60 + int(_ss)
                frame_no = seconds * self.get_fps()
            except Exception as e:
                print(e)
                logging.error("Video time string is incorrect: {}".format(video_time_str))
                sys.exit(1)
        return int(frame_no)

    def seek(self, timestamp: int):
        if timestamp < self.__frame_count:
            self.init_capture()

        if timestamp > self.__frame_count:
            while timestamp > self.__frame_count:
                self.__grab_frame()
            print(f"Seek done: {self.__frame_count}")
        else:
            print(f"Seek already done: {self.__frame_count}")
        return 0

    def seek_n_read(self, timestamp: int):
        self.seek(timestamp)
        return self.read_frame()

    def seek_time(self, time_str: str):
        hh, mm, ss = time_str.split(":")
        timestamp = (int(hh) * 3600 + int(mm) * 60 + int(ss)) * self.get_fps()
        return self.seek(timestamp)

    def __del__(self):
        self.cleanup()

    def save_clip(self, timestamp_from: int, timestamp_to: int) -> str:
        ...

    def cleanup(self):
        self.__cap.release()
        if self.pbar is not None:
            self.pbar.close()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    file_path = "/home/dulanj/MSc/DialogRugby/match-16.mp4"
    obj = VideoReader(file_path)
    print("FPS: ", obj.get_fps())
    print("Shape: ", obj.get_shape())
    print("Total frame count: ", obj.get_total_frame_count())
    print("Duration: ", obj.get_video_duration())
    obj.seek_time("00:30:09")
    obj.visualize()
