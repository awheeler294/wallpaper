#!/usr/bin/env python3
import argparse
import glob
import random
import sys
import subprocess
import json
from pathlib import Path

import unittest

# For each output randomly select a wallpaper from the wallpaper directory
# and apply it.
# Do not pick the same wallpapers for any displays wallpapers.
# If a directory for the current day exists, pick as many wallpapers as possible
# from it.

HOME = str(Path.home())

def get_paths(num_paths=1, base_path=HOME):
    paths = []
    for _ in range(num_paths):
        paths.append(choose_path(base_path, paths))
    return paths

def choose_path(base_path, excludes=[], sub_path=""):
    paths = [path for path in glob.glob(base_path + "/" + sub_path + "/*")
                if path not in excludes]
    return(random.choice(paths))

def get_outputs_from_sway():
    get_outputs = subprocess.run(['swaymsg', '-t', 'get_outputs'], text=True, capture_output=True)
    stdout = get_outputs.stdout
    return json.loads(stdout)

def get_output_names():
    return [output['name'] for output in get_outputs_from_sway()]

def set_wallpapers_for_sway(outputs, wallpaper_paths):
    for i in range(len(outputs)):
        subprocess.run(['swaymsg', 'output', outputs[i], 'background', wallpaper_paths[i], 'fill'])

def set_wallpapers(base_path):
    outputs = get_output_names()
    wallpaper_paths = get_paths(len(outputs), base_path)
    set_wallpapers_for_sway(outputs, wallpaper_paths)


class GetPathTestCase(unittest.TestCase):
    import os
    TEST_PATH = os.getcwd() + "/test-data"

    def test_choose_path_returns_a_valid_path(self):
        path = choose_path(self.TEST_PATH)
        paths = glob.glob(self.TEST_PATH + '/*')
        self.assertIn(path, paths)

    def test_choose_path_excludes_duplicates(self):
        num_paths = len(glob.glob(self.TEST_PATH + '/*'))

        paths = []
        for _ in range(num_paths):
            paths.append(choose_path(self.TEST_PATH, paths))

        self.assertEqual(len(paths), len(set(paths)))

    def test_get_paths_returns_valid_paths(self):
        test_paths = glob.glob(self.TEST_PATH + '/*')
        num_paths = random.randint(1, len(test_paths) - 1)
        paths = get_paths(num_paths, self.TEST_PATH)
        self.assertTrue(set(paths).issubset(set(test_paths)))

    def test_get_paths_excludes_duplicates(self):
        num_paths = len(glob.glob(self.TEST_PATH + '/*'))
        paths = get_paths(num_paths, self.TEST_PATH)
        self.assertEqual(len(paths), len(set(paths)))


if __name__=='__main__':
    parser = argparse.ArgumentParser(
        description='Set randomly chosen wallpapers for each output under swaywm')
    parser.add_argument('base_path', metavar='base-path', nargs='?',
                        default=HOME+'/Pictures/wallpapers',
                        help='Base path to find random paths in')

    args = parser.parse_args()

    set_wallpapers(args.base_path)
