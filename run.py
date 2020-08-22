#!/usr/bin/env python3

import argparse
from os.path import join, exists
from os import makedirs, remove
from glob import glob
import json
from time import time
import numpy as np
from tqdm import tqdm
from PIL import Image

import util


parser = argparse.ArgumentParser(description="Webpage monitor.")
parser.add_argument(
    '--roster_json', type=str, default='./roster.json', help="path to the roster")
parser.add_argument(
    '--check_every', type=int, default=600, help="check every N seconds")
parser.add_argument(
    '--exit_after', type=int, default=None, help="quit after N seconds")
parser.add_argument(
    '--tmp_dir', type=str, default='/tmp/webpage-monitor',
    help="directory to dump screenshots for comparison")


def main(args):
    if args.exit_after is None:
        exit_after = np.inf
    else:
        exit_after = args.exit_after

    roster = load_roster(args.roster_json)

    start_t = time()
    last_check_t = 0

    while True:
        if time() - last_check_t > args.check_every:
            changed = []

            for url, opt in tqdm(roster.items(), desc="Checking URLs"):
                out_dir = join(
                    args.tmp_dir,
                    url.replace('/', '_').replace('?', '_').replace('&', '_'))

                # Take screenshots
                screenshot(url, out_dir, opt)

                pngs = sorted(glob(join(out_dir, '*.png')))

                # Compare with previous screenshots
                if len(pngs) > 1:
                    if diff(*pngs[-2:]):
                        changed.append(url)

                # Remove earlier screenshots to avoid storage explosion
                if len(pngs) > 2:
                    for f in pngs[:-2]:
                        remove(f)

            last_check_t = time()

            # Email myself the results
            if changed:
                msg = '\n'.join(changed)
                util.email_myself(msg, subject="Webpage Monitor")
                util.format_print("Change detected; email sent", 'warn')
                # from IPython import embed; embed()

        if time() - start_t > exit_after:
            break


def diff(png1, png2, thres=0.1):
    im1 = Image.open(png1)
    im2 = Image.open(png2)
    im1 = np.array(im1)
    im2 = np.array(im2)

    # Check size
    if im1.shape != im2.shape:
        return True

    # Check content
    im1 = im1.astype(float) / np.iinfo(im1.dtype).max
    im2 = im2.astype(float) / np.iinfo(im2.dtype).max
    diff_im = np.abs(im1 - im2)
    return (diff_im >= thres).any()


def screenshot(url, out_dir, opt, width=1080, delay=3):
    if not exists(out_dir):
        makedirs(out_dir)

    cmd = (
        'webkit2png --fullsize --ignore-ssl-check --width={w} --delay={delay} '
        '--dir={dir_} --filename={t} {url}').format(
            w=width, delay=delay, dir_=out_dir, t=time(), url=url)
    util.call(cmd, silence_stdout=True)


def load_roster(roster_json):
    with open(roster_json, 'r') as h:
        roster = json.load(h)
    return roster


if __name__ == '__main__':
    main(parser.parse_args())
