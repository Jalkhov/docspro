import click
from octodir import Octodir


@click.command()
@click.option("--folder_url", prompt="Full folder url", help="Full url from the folder to download")
@click.option("--output_folder", prompt="Output folder", help="Folder where files will be downloaded")
def octodir_cli(folder_url, output_folder):
    x = Octodir(folder_url, output_folder)
    x.dowload_folder()


if __name__ == '__main__':
    octodir_cli()
