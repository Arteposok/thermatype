import click
import requests
@click.command()
@click.argument("ip")
@click.argument("text", type=click.File("r"), default="-")
def main(text: str, ip: str):
    requests.post(f"{ip}/print_text", json = {"text":f"{"".join(text).strip()}\n"})
main()
