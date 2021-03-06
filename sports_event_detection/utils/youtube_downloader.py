#!/usr/bin/env python3
"""
@Filename:    youtube_downloader.py
@Author:      dulanj
@Time:        31/01/2022 23:37
"""
import os

from pytube import YouTube


class YouTubeDownloader:
    def __init__(self, url):
        self.url = url
        self.yt = YouTube(url)

    def get_video_title(self):
        return self.yt.title.replace(" ", "_").replace("/", "_").replace("(", "_").replace(")", "_") \
                   .replace("&", "_").replace("|", "_").replace("'", "_").replace(".", "_") + ".mp4"

    def get_info(self):
        print("Title of video:   ", self.yt.title)
        print("Number of views:  ", self.yt.views)
        print("Length of video:  ", self.yt.length, "seconds")
        return {
            "title": self.yt.title,
            "views": self.yt.views,
            "length": self.yt.length
        }

    def download_video(self, path, filename=None, resolution="360p", overwrite=False):
        stream = list(self.yt.streams.filter(progressive=True))
        _full_path = None
        for _st in stream:
            res = _st.resolution
            if res == resolution:
                _filename = self.get_video_title() if filename is None else filename
                _full_path = os.path.join(path, _filename)
                print(f"Downloading video to: {_full_path} \n from {_st}")
                if os.path.isfile(_full_path) and not overwrite:
                    print(f"File already exists [{_filename}] in {path}")
                    return _full_path
                _st.download(path, _filename)
                print("Download complete! - {}".format(_filename))
                break
            else:
                print("Resolution not supported - ", res)
        return _full_path


if __name__ == '__main__':
    links = [
        "https://www.youtube.com/watch?v=OsMiN6QdiNw",
        "https://www.youtube.com/watch?v=HGPhsSsZE7E",
        "https://www.youtube.com/watch?v=hwn3NpEwBfk",
        "https://www.youtube.com/watch?v=WnrOpvy0U_w"
    ]
    for link in links:
        print("Downloading video: ", link)
        yt = YouTubeDownloader(link)
        yt.get_info()
        yt.download_video("video_downloads")
