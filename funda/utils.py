import typer


def positive_integer(value: str) -> int:
    try:
        ivalue = int(value)
        if ivalue < 0:
            raise ValueError()
        return ivalue
    except ValueError:
        raise typer.BadParameter("Must be a positive integer")


