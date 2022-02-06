import asyncio

import cv2
import numpy


def check_similarity(a: numpy.ndarray, b: numpy.ndarray, cut_line=0.8):
    similarity = get_similarity(a, b)
    return similarity >= cut_line


def get_similarity(a: numpy.ndarray, b: numpy.ndarray):
    hist_a = cv2.calcHist([a], [0, 1], None, [180, 256], [0, 180, 0, 256])
    cv2.normalize(hist_a, hist_a, 0, 1, cv2.NORM_MINMAX)
    hist_b = cv2.calcHist([b], [0, 1], None, [180, 256], [0, 180, 0, 256])

    return cv2.compareHist(hist_a, hist_b, cv2.HISTCMP_CORREL)


def image_search(src, template, accuracy=0.8):
    if src is None or template is None: return None
    h, w = template.shape
    if len(src.shape) == 3:
        src = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
    res = cv2.matchTemplate(src, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    # print(f'acc={max_val}')
    return None if max_val < accuracy else (max_loc[0], max_loc[1], w, h)

def image_search_from_bbox(src, bbox, template, accuracy=0.8):
    if src is None or template is None: return None
    h, w = template.shape
    if len(src.shape) == 3:
        src = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
    bbox_area = src[bbox[1]:bbox[1] + bbox[3], bbox[0]:bbox[0] + bbox[2]]
    cv2.imshow('bbox_area', bbox_area)
    res = cv2.matchTemplate(bbox_area, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    if max_val < accuracy: return None
    else: return max_loc[0] + bbox[0], max_loc[1] + bbox[1], w, h
