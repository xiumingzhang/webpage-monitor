import argparse
from os.path import join, exists
from os import makedirs, remove
from shutil import rmtree
from glob import glob
import json
from time import time
import datetime
import difflib
import requests
import numpy as np
from tqdm import tqdm

import util

parser = argparse.ArgumentParser(description='Webpage monitor.')
parser.add_argument('--roster_json',
                    type=str,
                    default='./roster.json',
                    help='path to the roster')
parser.add_argument('--email_addr',
                    type=str,
                    default='xiuming6zhang@gmail.com',
                    help='email address')
parser.add_argument('--check_every',
                    type=int,
                    default=43200,
                    help='check every N seconds')
parser.add_argument('--exit_after',
                    type=int,
                    default=None,
                    help='quit after N seconds')
parser.add_argument('--snapshot_dir',
                    type=str,
                    default='./snapshots',
                    help='directory to dump screenshots for comparison')
parser.add_argument('--clear_cached',
                    action='store_true',
                    help='whether to clear the screenshots on disk')


def main(args):
    exit_after = np.inf if args.exit_after is None else args.exit_after

    with open(args.roster_json, 'rb') as file_handle:
        roster = json.load(file_handle)

    start_t = time()
    last_check_t = 0

    if args.clear_cached and exists(args.snapshot_dir):
        rmtree(args.snapshot_dir)

    while True:
        if time() - last_check_t > args.check_every:
            changed, deltas = [], []

            pbar = tqdm(roster.items())
            for url, opt in pbar:
                pbar.set_description(f"Checking {url}")

                # Snapshot the current webpage.
                out_dir = join(args.snapshot_dir,
                               util.folder_name_from_url(url))
                snapshot(url, out_dir)

                # Compare with the previous snapshot.
                snapshot_paths = sorted(
                    glob(join(out_dir, '????_??_??_??_??_??.html')))
                if len(snapshot_paths) > 1:
                    delta = diff_snapshots(snapshot_paths[-2],
                                           snapshot_paths[-1], out_dir, opt)
                    if delta != '':
                        changed.append(url)
                        deltas.append(delta)

                # Remove earlier screenshots to avoid storage explosion
                if len(snapshot_paths) > 2:
                    for x in snapshot_paths[:-2]:
                        remove(x)

            last_check_t = time()

            # Email myself the results
            if changed:
                msg = ''
                for url, delta in zip(changed, deltas):
                    msg += f'------\n{url}\n\n{delta}\n\n\n'
                util.email_oneself(msg,
                                   args.email_addr,
                                   subject='Webpage Monitor')
                util.format_print('Change detected; email sent', 'header')

            if time() - start_t > exit_after:
                break


def diff_snapshots(html0_path, html1_path, out_dir, opt):
    # Parse URL-specific options.
    ignore_prefices = opt.get('ignore_prefix')
    if ignore_prefices is None:
        ignore_prefices = []
    if isinstance(ignore_prefices, str):
        ignore_prefices = [ignore_prefices]
    ignore_prefices = tuple(ignore_prefices)
    # Diff the two HTMLs.
    html0_content = util.read_file(html0_path)
    html1_content = util.read_file(html1_path)
    delta = difflib.ndiff(html0_content.split('\n'), html1_content.split('\n'))
    # Keep differences only.
    delta = [x for x in delta if x.startswith(('+ ', '- '))]
    # Ignore
    filtered_delta = [
        x for x in delta
        if not x.lstrip('+ ').lstrip('- ').startswith(ignore_prefices)
    ]
    filtered_delta = '\n'.join(filtered_delta)
    delta_path = join(out_dir, 'delta.html')
    util.write_file(filtered_delta, delta_path)
    return filtered_delta


def snapshot(url, out_dir):
    request = requests.get(url)
    html_src = request.content.decode()
    if not exists(out_dir):
        makedirs(out_dir)
    timestamp = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
    html_path = join(out_dir, timestamp + '.html')
    util.write_file(html_src, html_path)


if __name__ == '__main__':
    main(parser.parse_args())
