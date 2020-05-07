#!/usr/bin/env python

import click
import sys
import os

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/..")

from olympia import ROOT_DIR


from bin.commands.train import train
from bin.commands.scrape import scrape


@click.group()
def cli():
    pass


cli.add_command(train)
cli.add_command(scrape)

if __name__ == "__main__":
    cli()
