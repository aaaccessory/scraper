
from cleantext import clean
import datetime
import calendar
import re

def add_months(sourcedate, months):
    month = sourcedate.month - 1 + months
    year = sourcedate.year + month // 12
    month = month % 12 + 1
    day = min(sourcedate.day, calendar.monthrange(year,month)[1])
    return datetime.date(year, month, day)

def get_text_by_max_length(dict):
    values_view = dict.values()
    value_iterator = iter(values_view)
    first_value = next(value_iterator)
    text = first_value
    for key in dict:
        if len(text) < len(dict[key]):
            text = dict[key]

    return text

def give_emoji_free_text(text):
    # allchars = [str for str in text.decode('utf-8')]
    # emoji_list = [c for c in allchars if c in emoji.UNICODE_EMOJI]
    # clean_text = ' '.join([str for str in text.decode('utf-8').split() if not any(i in str for i in emoji_list)])
    clean_text = clean(text, no_emoji=True)
    clean_text = clean_text.encode('utf-8','ignore').decode("utf-8")
    clean_text = re.sub(r'[^\x00-\x7f]', r'', clean_text)
    return clean_text
