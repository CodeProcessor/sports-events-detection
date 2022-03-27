#!/usr/bin/env python3
"""
@Filename:    storage.py
@Author:      dulanj
@Time:        23/01/2022 17:46
"""
import json
import logging
import os
import sqlite3 as sl


class Storage:
    def __init__(self, db_name):
        init = not os.path.exists(db_name)
        _db_dir = os.path.dirname(db_name)
        if not os.path.exists(_db_dir):
            os.makedirs(_db_dir)
        self.con = sl.connect(db_name)
        self.cur = self.con.cursor()
        if init:
            self.create_table()

    def create_table(self):
        self.cur.execute("""
                CREATE TABLE DATA (
                    frame_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    data TEXT
                );
            """)
        self.con.commit()

    def insert_data(self, frame_id, data):
        try:
            sql = 'INSERT INTO DATA (frame_id, data) values(?, ?)'
            data = [
                (frame_id, json.dumps(data))
            ]
            self.cur.executemany(sql, data)
            self.con.commit()
        except sl.IntegrityError:
            logging.error('Duplicate frame_id: {}'.format(frame_id))

    def insert_bulk_data(self, bulk_data):
        try:
            sql = 'INSERT INTO DATA (frame_id, data) values(?, ?)'
            data = [
                (int(item["frame_id"]), json.dumps(item)) for item in bulk_data
            ]
            self.cur.executemany(sql, data)
            self.con.commit()
        except sl.IntegrityError:
            logging.error('Duplicate frame_id')

    def delete_bulk_data(self, frame_id_list):
        sql = 'DELETE FROM DATA WHERE frame_id = ?'
        data = [
            (int(frame_id),) for frame_id in frame_id_list
        ]
        self.cur.executemany(sql, data)
        self.con.commit()

    def get_data(self, frame_id):
        sql = 'SELECT data FROM DATA WHERE frame_id = ?'
        data = self.con.execute(sql, (frame_id,)).fetchone()
        return json.loads(data[0]) if data is not None else None

    def update_data(self, frame_id, data):
        sql = 'UPDATE DATA SET data = ? WHERE frame_id = ?'
        self.cur.execute(sql, (json.dumps(data), frame_id))
        self.con.commit()

    def __del__(self):
        self.con.close()


if __name__ == '__main__':
    storage = Storage('storage_1.db')
    storage.insert_bulk_data([{'frame_id': 1, 'data': {'a': 1}}, {'frame_id': 2, 'data': {'a': 2}}])
    print(storage.get_data(1))
    print(storage.get_data(2))
    print(storage.get_data(3))
    storage.update_data(1, {'a': 3, 'b': 4})
    print(storage.get_data(1))
    print(storage.get_data(2))
    print(storage.get_data(3))
