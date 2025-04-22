from datetime import datetime


def pretty_sum(amount) -> str:
    if amount:
        return f"{amount:,.1f}".replace(",", " ")
    else:
        return f"0.0"


def pretty_datetime(date):
    if date:
        formated_date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S.%f")
        return formated_date.strftime("%d.%m.%Y %H:%M")
    else:
        return "N/A"

