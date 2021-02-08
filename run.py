#!/usr/bin/env python3

import argparse
from os.path import join, exists
from os import makedirs, remove
from shutil import rmtree
from glob import glob
import json
from time import time
import numpy as np
from scipy.ndimage import gaussian_filter
from tqdm import tqdm

import util


parser = argparse.ArgumentParser(description="Webpage monitor.")
parser.add_argument(
    '--roster_json', type=str, default='./roster.json', help="path to the roster")
parser.add_argument(
    '--check_every', type=int, default=43200, help="check every N seconds")
parser.add_argument(
    '--exit_after', type=int, default=None, help="quit after N seconds")
parser.add_argument(
    '--tmp_dir', type=str, default='/tmp/webpage-monitor',
    help="directory to dump screenshots for comparison")
parser.add_argument(
    '--clear_cached', action='store_true',
    help="whether to clear the screenshots on disk")


def main(args):
    if args.exit_after is None:
        exit_after = np.inf
    else:
        exit_after = args.exit_after

    roster = load_roster(args.roster_json)

    start_t = time()
    last_check_t = 0

    if args.clear_cached and exists(args.tmp_dir):
        rmtree(args.tmp_dir)

    while True:
        if time() - last_check_t > args.check_every:
            changed, deltas = [], []

            for url, opt in tqdm(roster.items(), desc="Checking URLs"):
                out_dir = join(
                    args.tmp_dir, replace_special_char(url)).rstrip('/')

                # Take screenshots
                screenshot(url, out_dir, opt)

                pngs = sorted(glob(join(out_dir, '*.png')))

                # Compare with previous screenshots
                if len(pngs) > 1:
                    delta_png = out_dir + '_delta.png'
                    delta = diff_screenshots(*pngs[-2:], delta_png)
                    if delta is not None:
                        changed.append(url)
                        deltas.append(delta)

                # Remove earlier screenshots to avoid storage explosion
                if len(pngs) > 2:
                    for f in pngs[:-2]:
                        remove(f)

            last_check_t = time()

            # Email myself the results
            if changed:
                msg = ''
                for url, delta in zip(changed, deltas):
                    msg += "file://{delta}\n{url}\n\n".format(
                        delta=delta, url=url)
                util.email_myself(msg, subject="Webpage Monitor")
                util.format_print("Change detected; email sent", 'header')
                # from IPython import embed; embed()

        if time() - start_t > exit_after:
            break


def diff_screenshots(
        old_png, new_png, delta_png, pix_diff_thres=0.1, n_diff_thres=16,
        unchanged_alpha=0.2, diff_blur_sigma=4):
    old = util.imread_arr(old_png)
    new = util.imread_arr(new_png)

    # Sizes are even different
    if old.shape != new.shape:
        util.imwrite_arr(new, delta_png)
        return delta_png

    # Check content
    pixel_is_diff = np.abs(old - new) >= pix_diff_thres # (H, W, 3)
    pixel_is_diff = np.sum(pixel_is_diff, axis=2) > 0

    # Not enough different pixels for a change
    if np.sum(pixel_is_diff) <= n_diff_thres:
        return None

    # Highlight the changed part
    alpha = unchanged_alpha * np.ones_like(new)
    alpha[np.dstack([pixel_is_diff] * 3)] = 1
    alpha = gaussian_filter(alpha, diff_blur_sigma)
    delta = alpha * new + (1 - alpha) * np.zeros_like(new)
    util.imwrite_arr(delta, delta_png)
    return delta_png


def screenshot(url, out_dir, opt, width=512, delay=3):
    if not exists(out_dir):
        makedirs(out_dir)

    cmd = (
        'webkit2png --fullsize --no-images --ignore-ssl-check --width={w} '
        '--delay={delay} --dir={dir_} --filename={t} {url}').format(
            w=width, delay=delay, dir_=out_dir, t=time(), url=url)
    util.call(cmd, silence_stdout=True)


def load_roster(roster_json):
    with open(roster_json, 'r') as h:
        roster = json.load(h)
    return roster


def replace_special_char(url):
    return url.replace(
        '/', '_').replace('?', '_').replace('&', '_').replace(':', '_')


if __name__ == '__main__':
    main(parser.parse_args())
