import click


@click.group()
def train():
	pass


@stocks.command()
#@click.argument("equity_id", type=int)
@inject
def train_duration():
    pass
