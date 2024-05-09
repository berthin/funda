import typer

app = typer.Typer()


@app.command()
def main():
    print('typer app')

if __name__ == '__main__':
    app()
