#!/usr/bin/env python3
"""
@Filename:    test_overall_accuracy.py
@Author:      dulanj
@Time:        09/04/2022 17:30
"""
import pytest

from training_pipeline.step4_evaluation.overall_accuracy import check_overlap


@pytest.mark.parametrize("series_a, series_b, is_overlap",
                         [
                             (
                                     {"start_time": "10:11", "end_time": "10:12"},
                                     {"start_time": "10:11", "end_time": "10:12"},
                                     True
                             ),
                             (
                                     {"start_time": "00:11:02", "end_time": "00:11:11"},
                                     {"start_time": "00:10:36", "end_time": "00:12:59"},
                                     True
                             ),
                             (
                                     {"start_time": "00:11:02", "end_time": "00:11:11"},
                                     {"start_time": "00:11:36", "end_time": "00:12:59"},
                                     False
                             ),
                         ]
                         )
def test_check_overlap(series_a, series_b, is_overlap):
    assert check_overlap(series_a, series_b)[0] == is_overlap
