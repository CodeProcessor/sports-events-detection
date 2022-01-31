#!/usr/bin/env python3
"""
@Filename:    youtube_downloader.py
@Author:      dulanj
@Time:        31/01/2022 23:37
"""
from pytube import YouTube


class YouTubeDownloader:
    def __init__(self, url):
        self.url = url
        self.yt = YouTube(url)

    def get_video_title(self):
        return self.yt.title.replace(" ", "_").replace("/", "_") + ".mp4"

    def get_info(self):
        print("Title of video:   ", self.yt.title)
        print("Number of views:  ", self.yt.views)
        print("Length of video:  ", self.yt.length, "seconds")

    def download(self, path, filename=None, resolution="360p"):
        stream = list(self.yt.streams.filter(progressive=True))
        for _st in stream:
            res = _st.resolution
            if res == resolution:
                print(f"Downloading video: {_st}")
                if filename is None:
                    _st.download(path)
                else:
                    _st.download(path, filename)
                print("Download complete!")
                break
            else:
                print("Resolution not supported - ", res)


if __name__ == '__main__':
    yt = YouTubeDownloader("https://www.youtube.com/watch?v=nnpW8O5YLkM")
    yt.get_info()
    yt.download("video_downloads")
