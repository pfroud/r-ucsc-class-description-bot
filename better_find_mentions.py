"""
Working on making a thing to see mentions of same department with list of numbers.
Strings I'm using for testing:

115, 116, and 117
115a, 116g, and 117m
111 & 102
46, 170 or 80
15/16
15a/16a
1 and 2
4, 1, and 2
"""

import re
from find_mentions import _unify_mention_format

depts = "acen|ams|anth|aplx|art|artg|astr|bioc|bme|ce|chem|chin|clei|clni|clte|cmmu|cmpe|cmpm|cmps|cowl|cres|crwn|cs|" \
        "danm|eart|econ|educ|ee|eeb|envs|film|fmst|fren|game|germ|gree|havc|hebr|his|hisc|ital|japn|jwst|krsg|laad|" \
        "lals|latn|lgst|ling|lit|ltcr|ltel|ltfr|ltge|ltgr|ltin|ltit|ltmo|ltpr|ltsp|ltwl|math|mcdb|merr|metx|musc|" \
        "oaks|ocea|phil|phye|phys|poli|port|prtr|psyc|punj|russ|scic|socd|socy|span|sphs|stev|thea|tim|ucdc|writ|yidd"

same_num_list_letters = " ?(\d+([A-Za-z] ?/ ?)+[A-Za-z])"
num_with_optional_letter = "(\d+[A-Za-z]?)"
mention = "(" + same_num_list_letters + "|" + num_with_optional_letter + ")"

delim = "([,/ &+]|or|and|with)*"

final = "(" + mention + delim + ")+"


# final is:
# "(((\d+([A-Za-z] ?/ ?)+[A-Za-z])|(\d+[A-Za-z]?))([,/ &+]|or|and|with)*)+"


def handle_list_letters(dept, rest):
    """Gets a string like '129A/B/C' and returns something like ['129A', '129B', '129C']

    :param dept:
    :param rest:
    :return:
    """

    # print("running on \"{}\", \"{}\"".format(dept, rest))

    m = re.match(" ?(\d+) ?((?:[A-Za-z] ?/ ?)+[A-Za-z])", rest)
    num = m.group(1)
    letters = m.group(2).split('/')

    # print("\"{}\"".format(num))
    # print(letters)

    return_list = []

    for l in letters:
        return_list.append(dept + " " + num + l.strip())

    return return_list


def parse_string(str_):
    """I'm not sure what this will do.

    :param str_:
    :return:
    """
    if not str_:
        return []

    match_dept = re.search(depts, str_, re.IGNORECASE)

    if not match_dept:
        return []

    dept = str_[match_dept.start():match_dept.end()].lower()
    if dept == 'cs':
        dept = 'cmps'
    if dept == 'ce':
        dept = 'cmpe'
    # print("\"{}\"".format(dept))

    rest = str_[match_dept.end():]
    # print("\"{}\"".format(rest))

    mentions = []

    match_list_letters = re.match(same_num_list_letters, rest)
    if match_list_letters:
        mentions.extend(handle_list_letters(dept, rest))

    print(mentions)


parse_string("I am going to take CS 10a/b/c")
