import os
import argparse

CRAWLER_TEMPLATE = """
__author__ = "{author}"

from crawlster.core import Crawlster
from crawlster.result_handler import ResultHandler


class {name_capitalized}ResultHandler(ResultHandler):

    fields = {{
        "field_name": str  # the type of the field
    }}

    def save_result(self, **values):
        # do something with the results
        pass


class {name_capitalized}Crawler(Crawlster):

    worker_threads = 4

    result_handlers = [
        {name_capitalized}ResultHandler
    ]

    start_steps = [
        ("", "start_step")
    ]

    def start_step(self, url):
        next_url = ""
        self.schedule_step(self.implement_me, next_url)

    def implement_me(self, url):
        raise NotImplemented("Implement me")

"""


def create_new_parser(name, author):
    with open("{}_crawler.py".format(name), "w") as f:
        f.write(CRAWLER_TEMPLATE.format(
            name=name,
            name_capitalized=name.capitalize(),
            author=author
        ))


def main():
    parser = argparse.ArgumentParser(prog="crawlster", description="Crawlster utilities")

    subparsers = parser.add_subparsers()

    subparser_newparser = subparsers.add_parser("newparser", help="Create a new parser",
                                                description="Crate a new parser")
    subparser_newparser.add_argument("name", help="The name of the parser")
    subparser_newparser.add_argument("--author", default="Anonymous")

    args = parser.parse_args()
    create_new_parser(args.name, args.author)


main()
