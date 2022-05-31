from os.path import join, exists
from os import makedirs, remove
from shutil import rmtree
from glob import glob
import json
from time import time
import datetime
import difflib
from absl import app, flags, logging
import requests
import numpy as np
from tqdm import tqdm

import util

FLAGS = flags.FLAGS
flags.DEFINE_string('roster_json', './roster.json', 'path to the roster')
flags.DEFINE_string('gmail', 'xiuming6zhang@gmail.com', 'email address')
flags.DEFINE_integer('check_every', 43200, 'check every N seconds')
flags.DEFINE_integer('exit_after', None, 'quit after N seconds')
flags.DEFINE_string('snapshot_dir', './snapshots',
                    'directory to dump screenshots for comparison')
flags.DEFINE_boolean('clear_cached', False,
                     'whether to clear the screenshots on disk')


def main(_):
    exit_after = np.inf if FLAGS.exit_after is None else FLAGS.exit_after

    with open(FLAGS.roster_json, 'rb') as file_handle:
        roster = json.load(file_handle)

    start_t = time()
    last_check_t = 0

    if FLAGS.clear_cached and exists(FLAGS.snapshot_dir):
        rmtree(FLAGS.snapshot_dir)

    while True:
        if time() - last_check_t > FLAGS.check_every:
            changed, deltas = [], []

            pbar = tqdm(roster.items())
            for url, opt in pbar:
                pbar.set_description(f"Checking {url}")

                # Snapshot the current webpage.
                out_dir = join(FLAGS.snapshot_dir,
                               util.folder_name_from_url(url))
                success = snapshot(url, out_dir)
                if not success:
                    continue

                # Compare with the previous snapshot.
                snapshot_paths = sorted(
                    glob(join(out_dir, '????_??_??_??_??_??.html')))
                if len(snapshot_paths) > 1:
                    delta = diff_snapshots(snapshot_paths[-2],
                                           snapshot_paths[-1], out_dir, opt)
                    if delta != '':
                        changed.append(url)
                        deltas.append(delta)

                # Remove earlier screenshots to avoid storage explosion.
                if len(snapshot_paths) > 2:
                    for snapshot_path in snapshot_paths[:-2]:
                        remove(snapshot_path)

            last_check_t = time()

            # Email myself the results.
            if changed:
                msg = ''
                for url, delta in zip(changed, deltas):
                    msg += f'------\n{url}\n\n{delta}\n\n\n'
                util.email_oneself(msg, FLAGS.gmail, subject='Webpage Monitor')

                logging.info('Change detected; email sent')
            else:
                logging.info('No change detected')

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
    # Ignore specified patterns.
    filtered_delta = [
        x for x in delta
        if not x.lstrip('+ ').lstrip('- ').startswith(ignore_prefices)
    ]
    filtered_delta = '\n'.join(filtered_delta)
    delta_path = join(out_dir, 'delta.html')
    util.write_file(filtered_delta, delta_path)
    return filtered_delta


def snapshot(url, out_dir):
    try:
        request = requests.get(url)
    except requests.exceptions.ConnectionError:
        logging.warn(f'Connection Error: {url}; ignored')
        return False
    html_src = request.content.decode()
    if not exists(out_dir):
        makedirs(out_dir)
    timestamp = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
    html_path = join(out_dir, timestamp + '.html')
    util.write_file(html_src, html_path)
    return True


if __name__ == '__main__':
    app.run(main)
