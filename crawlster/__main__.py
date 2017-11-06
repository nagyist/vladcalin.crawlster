import sys
import os
import argparse
import inspect

import colorama

from crawlster.core import Crawlster

colorama.init()

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


def run_parser_from_source(source):
    if os.path.isdir(source):

        for root, dirs, files in os.walk(source):
            for filename in files:
                if filename.endswith(".py"):
                    run_parser_from_source(os.path.join(root, filename))
        return

    import importlib.util
    module_name = os.path.split(source)[-1].split(".")[0]

    # load the module
    specs = importlib.util.spec_from_file_location(
        "loaded_crawler.{}".format(module_name),
        source)
    module = importlib.util.module_from_spec(specs)
    specs.loader.exec_module(module)

    crawlers = []
    for item_name in dir(module):
        item = getattr(module, item_name)
        if not inspect.isclass(item):
            continue

        if issubclass(item, Crawlster) and type(item) != Crawlster:
            print("Found crawler: {}".format(item))
            crawlers.append(item)

    if not crawlers:
        print(colorama.Fore.RED + "Couldn't find any crawlers in {}".format(
            source))
        sys.exit(-1)

    for crawler in crawlers:
        instance = crawler()
        instance.start()


def make_new_parser_subparser(subparsers):
    subparser_newparser = subparsers.add_parser(
        "newparser",
        help="Create a new parser",
        description="Crate a new parser")
    subparser_newparser.add_argument("name", help="The name of the parser")
    subparser_newparser.add_argument("--author", default="")


def make_run_parser_subparser(subparsers):
    subparser_run = subparsers.add_parser("run",
                                          help="Runs a crawler from a file")

    subparser_run.add_argument(
        "source",
        help="The source file that contains the crawler")


def main():
    parser = argparse.ArgumentParser(prog="crawlster",
                                     description="Crawlster utilities")

    subparsers = parser.add_subparsers(dest="action")

    make_new_parser_subparser(subparsers)
    make_run_parser_subparser(subparsers)

    args = parser.parse_args()
    if not hasattr(args, "action") or not args.action:
        parser.print_help()
        sys.exit(-1)

    if args.action == "newparser":
        create_new_parser(args.name, args.author)
    elif args.action == "run":
        run_parser_from_source(args.source)


main()
