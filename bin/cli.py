#!/usr/bin/env python

import click

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/..")

from bin.commands.train import train


@click.group()
def cli():
    pass


cli.add_command(train)

if __name__ == "__main__":
    cli()
