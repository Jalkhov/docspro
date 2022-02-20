import datetime

def now():
    return datetime.datetime.now()


def today_date():
    return now().strftime("%d-%m-%Y")


def today_time():
    return now().strftime("%I:%M:%S %p")


def today():
    date = today_date()
    time = today_time()

    return f'{date} {time}'
