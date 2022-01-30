#!/usr/bin/env python3
"""
@Filename:    storage_edits.py
@Author:      dulanj
@Time:        27/01/2022 22:20
"""
from sports_event_detection.storage import Storage

if __name__ == '__main__':
    storage = Storage('Match#16_CR_&_FC_v_Army_SC_DRL_2019_20_event.db')
    storage_updated = Storage('Match#16_CR_&_FC_v_Army_SC_DRL_2019_20_event_n.db')
    frame_id = 1
    data = storage.get_data(frame_id)
    bulk_data = []
    while data is not None:
        data["data"] = data.pop("scrum_lineout_pred")
        bulk_data.append(data)

        if len(bulk_data) > 5000:
            storage_updated.insert_bulk_data(bulk_data)
            bulk_data = []

        print("Frame id: {}".format(frame_id))
        frame_id += 1
        data = storage.get_data(frame_id)

    storage_updated.insert_bulk_data(bulk_data)
    print('Done')
