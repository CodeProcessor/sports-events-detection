#!/usr/bin/env python3
"""
@Filename:    rename_videos.py
@Author:      dulanj
@Time:        14/01/2022 10:57
"""
import logging
import os


def main(path_to_videos):
    for root, dirs, files in os.walk(path_to_videos):
        if root == path_to_videos:
            for file in files:
                if file.endswith('.mp4'):
                    try:
                        if file[:5] == "Match":
                            print('Skipped: {}'.format(file))
                            continue
                        _file = file.replace('-', ' ').replace('Match', ' ')
                        _file = _file.replace('   ', ' ').replace('  ', ' ').replace(' ', '_')
                        _file = _file.replace('_-_', '_')
                        _name, _id = _file.split('_#')
                        _match_id, ext = _id.split('.')
                        new_file_name = 'Match#{}_{}.{}'.format(int(_match_id), _name.strip(), ext)
                    except ValueError:
                        logging.error('Error: {}'.format(file))
                        continue
                    print("Renaming | {} >> {}".format(file, new_file_name))
                    os.rename(os.path.join(root, file), os.path.join(root, new_file_name))


if __name__ == '__main__':
    main(path_to_videos='/home/dulanj/MSc/DialogRugby')
