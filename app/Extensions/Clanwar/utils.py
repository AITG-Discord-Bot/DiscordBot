from datetime import datetime, timedelta


def convert_time(timestr, timeoffset):
    """Convert time to UTC"""
    try:
        for timeformat in [
            "%Y-%m-%d %H:%M",
            "%d/%m/%Y %H:%M",
            "%d %b %Y %H:%M",
            "%a %d %b %Y %H:%M",
            "%A %d %b %Y %H:%M",
            "%m/%d/%Y %H:%M",
        ]:
            partytime = datetime.strptime(timestr, timeformat)
            partytime = partytime + timedelta(hours=-timeoffset)
            break
    except ValueError:
        return None
    return partytime.strftime("%Y-%m-%d %H:%M")
