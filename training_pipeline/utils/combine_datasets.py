#!/usr/bin/env python3
"""
@Filename:    combine_datasets.py
@Author:      dulanj
@Time:        15/01/2022 10:18
"""
import os
import shutil

scrum_dataset = "/home/dulanj/MSc/sports-events-detection/training_pipeline/data/Rugby-Scrum-V2.v2i.yolov5pytorch"
lineout_dataset = "/home/dulanj/MSc/sports-events-detection/training_pipeline/data/Rugby-Lineout-v2.v2i.yolov5pytorch"
ruck_dataset = "/home/dulanj/MSc/sports-events-detection/training_pipeline/data/Rugby-Ruck.v3i.yolov5pytorch"
destination = "/home/dulanj/MSc/sports-events-detection/training_pipeline/data/Rugby-Scrum-Lineout-Ruck-V2.v3i.yolov5pytorch"


def get_id(dataset_path):
    if dataset_path == scrum_dataset:
        return 0
    elif dataset_path == lineout_dataset:
        return 1
    elif dataset_path == ruck_dataset:
        return 2
    else:
        raise ValueError("Dataset path is not valid")


def combine_datasets():
    if os.path.exists(destination):
        shutil.rmtree(destination)
    os.makedirs(destination)

    for dataset in [scrum_dataset, lineout_dataset, ruck_dataset]:
        ds_idx = get_id(dataset)
        for root, dirs, files in os.walk(dataset):
            for dir1 in ["train", "valid", "test"]:
                for dir2 in ["images", "labels"]:
                    root_path = os.path.join(dir1, dir2)
                    if root_path in root:
                        print(root)
                        print(files)
                        for file in files:
                            source = os.path.join(root, file)
                            dest_dir = os.path.join(destination, dir1, dir2)
                            if not os.path.exists(dest_dir):
                                os.makedirs(dest_dir)
                            print(source)
                            print(dest_dir)
                            if not file.endswith(".txt"):
                                txt_file_path = source.replace(".jpg", ".txt").replace("images", "labels")
                                if os.path.exists(txt_file_path):
                                    shutil.copy(source, os.path.join(dest_dir, file))
                            else:
                                with open(source, "r") as f:
                                    lines = f.readlines()
                                    with open(os.path.join(dest_dir, file), "w") as f:
                                        for line in lines:
                                            split_line = line.split()
                                            new_line = f"{ds_idx} " + " ".join(split_line[1:])
                                            f.write(new_line)


if __name__ == '__main__':
    combine_datasets()
