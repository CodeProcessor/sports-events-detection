"""

"""
import argparse
import enum
import os.path
import random
import shutil
import time
from glob import glob


class Names(enum.Enum):
    train = 0
    test = 1
    val = 0


split_ratio = {'train': 0.8, 'test': 0.1, 'val': 0.1}


def check_split_ratio():
    assert split_ratio['train'] + split_ratio['test'] + split_ratio['val'] > 0.99


def get_no_of_fies(file_length):
    train_length = int(file_length * split_ratio['train']) if split_ratio['train'] <= 1 else min(int(split_ratio['train']), file_length)
    test_length = int(file_length * split_ratio['test']) if split_ratio['test'] <= 1 else min(int(split_ratio['test']), file_length)
    val_length = int(file_length * split_ratio['val']) if split_ratio['val'] <= 1 else min(int(split_ratio['val']), file_length)

    excess = file_length - train_length - test_length - val_length
    if 2 > excess > 0:
        val_length += excess

    ret = {'train': train_length, 'test': test_length, 'val': val_length}
    return ret


def create_dir(path):
    if os.path.exists(path):
        shutil.rmtree(path)
    os.makedirs(path)


def split(source, destination):
    create_dir(destination)
    fp = open(os.path.join(destination, 'readme.md'), 'w')
    msg = "{:15}: {}\n{:15}: {}\n".format("Source", os.path.abspath(source), "Destination",
                                          os.path.abspath(destination))
    fp.write(msg)
    summary = ""
    try:
        random.seed(28)
        check_split_ratio()
        summary += "======================================\n"
        for _class_dir in glob(source + "/*"):
            if not os.path.isdir(_class_dir):
                continue
            _class_name = os.path.basename(_class_dir)
            _file_list = glob(os.path.join(source, _class_name) + "/*.*")
            random.shuffle(_file_list)
            list_length = len(_file_list)
            file_indexes = get_no_of_fies(list_length)
            summary += "Class {} contains {} images\n".format(_class_name, list_length)
            for _ttv in ['train', 'test', 'val']:
                dest_directory = os.path.join(destination, _ttv, _class_name)
                create_dir(dest_directory)
                _count = file_indexes[_ttv]
                print("Copying {} images - {} ...".format(_ttv, _count))
                time.sleep(1)
                for i, file_path in enumerate(_file_list):
                    if i < _count:
                        shutil.copy(file_path, dest_directory)
                        print("{} - {}/{} | {} > {}".format(_ttv, i + 1, _count, file_path, dest_directory))
                    else:
                        summary += "{} files copied to {} directory\n".format(_count, _ttv)
                        break
            summary += "---------------------------------------\n"
        summary += "======================================\n"
        print(summary)
    except Exception as e:
        print(e)
    finally:
        fp.write(summary)
        fp.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--src', metavar='-s', type=str, help='Path to source dataset', required=True)
    parser.add_argument('--dst', metavar='-d', type=str, help='Path to the destination path', required=True)
    args = parser.parse_args()
    _source = args.src
    _destination = args.dst
    split(_source, _destination)
