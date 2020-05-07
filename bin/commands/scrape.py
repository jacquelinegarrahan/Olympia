import click
from olympia.scripts import scrape_source


@click.group()
def scrape():
    pass


@scrape.command()
def scrape_midiworld():
    scrape_source.scrape_midiworld_midis()
