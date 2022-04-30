import argparse
from ptracking.scraping.fetch import fetch
from ptracking.preprocess import update_processed_content
from ptracking.debates.insert_debate import runDebateFetcher

parser = argparse.ArgumentParser()
parser.add_argument("command", type=str, choices=["scrape", "preprocess","debate"])
args = parser.parse_args()
if args.command == "scrape":
    fetch()

if args.command == "preprocess":
    print("Updating the pre-processed content field for all petitions")
    update_processed_content()
    print("Done!")

if args.command == "debate":
    print("Fetching debates starting with 1st January 2010")
    runDebateFetcher()
    print("Done!")