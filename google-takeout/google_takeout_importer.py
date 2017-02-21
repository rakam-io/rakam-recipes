import argparse
import json
import os

import requests

parser = argparse.ArgumentParser(description='Collects your past Google search events to Rakam API.')
parser.add_argument('--rakam-collection', default="google_search",
                    help='Rakam write key')
parser.add_argument('--rakam-write-key',
                    help='Rakam write key')
parser.add_argument('--rakam-api-url', default="https://app.rakam.io",
                    help='Rakam API address')
parser.add_argument('--search-dir',
                    help='Your Google Takeout search history directory')
args = parser.parse_args()


def collect_event(context, events):
    response = requests.post(context.get('rakam_api_url') + "/event/batch",
                             data=json.dumps(
                                 {'events': events, 'api': {'api_key': context.get('rakam_write_key')}}),
                             headers={'Content-type': 'application/json'})

    if response.status_code != 200:
        print('[{}] Invalid status code from Rakam {} with response {}'
              .format('google search', response.status_code, response.text))
    else:
        print("[{}] collected {} events between {} and {}."
              .format('google search', len(events), events[0].get('properties').get('_time'),
                      events[len(events) - 1].get('properties').get('_time')))


def convert_google(context, search_file):
    events = []

    with open(search_file, 'r') as handler:
        raw_events = json.loads(handler.read()).get('event')
        for event in raw_events:
            query = event.get('query')
            search_term = query.get('query_text')

            for timestamps in query.get('id'):
                events.append({"collection": context.get('rakam_collection'), "properties":
                    {"search_term": search_term,
                     "_time": int(timestamps.get('timestamp_usec')) / 1000,
                     "_user": "1"}})
        collect_event(context, events)


if __name__ == "__main__":
    _context = {'rakam_api_url': args.rakam_api_url, 'rakam_collection': args.rakam_collection,
                'rakam_write_key': args.rakam_write_key}
    for f in os.listdir(args.search_dir):
        convert_google(_context, os.path.join(args.search_dir, f))
