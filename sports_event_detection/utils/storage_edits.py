#!/usr/bin/env python3
"""
@Filename:    storage_edits.py
@Author:      dulanj
@Time:        27/01/2022 22:20
"""
from sports_event_detection.extras.common import ModelNames
from sports_event_detection.utils.storage import Storage

if __name__ == '__main__':
    storage = Storage('data_storage/Match#16_CR_&_FC_v_Army_SC_DRL_2019_20_play_n.db')
    storage_updated = Storage('data_storage/Match#16_CR_&_FC_v_Army_SC_DRL_2019_20.db')
    frame_id = 1
    data = storage.get_data(frame_id)
    bulk_data = []
    delete_frame_ids = []
    while data is not None:
        if isinstance(data["data"], dict):
            data["data"][f"{ModelNames.digital_object_detection_model.name}"] = data.pop("data")
        else:
            data["data"] = {f"{ModelNames.digital_object_detection_model.name}": data.pop("data")}
        bulk_data.append(data)
        delete_frame_ids.append(frame_id)

        if len(bulk_data) > 5000:
            storage_updated.delete_bulk_data(delete_frame_ids)
            storage_updated.insert_bulk_data(bulk_data)
            bulk_data = []

        print("Frame id: {}".format(frame_id))
        frame_id += 1
        data = storage.get_data(frame_id)

    storage_updated.insert_bulk_data(bulk_data)
    print('Done')
