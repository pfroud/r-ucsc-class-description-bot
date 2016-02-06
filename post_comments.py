"""
l
"""

import build_database
import tools
import pickle
import os.path

from build_database import CourseDatabase, Department, Course  # need this to de-pickle course_database.pickle
from find_mentions import PostWithMentions  # need this to de-pickle found_mentions.pickle


class ExistingComment:
    """Info about an existing comment with class info."""

    def __init__(self, comment_id_, mentions_):
        self.comment_id = comment_id_
        self.mentions_list = mentions_

    def __str__(self):
        return "\"{}\"->\"{}\"".format(self.comment_id, self.mentions_list)


def print_csv_row(submission_, action, mentions_current, mentions_previous):
    """Prints a CSV row to stdout to be used as a log about what happened with a comment.

    :param submission_: Submission object that you are commenting on
    :type submission_:  praw.objects.Submission
    :param action: string describing the action taken
    :type action: str
    :param mentions_current: list of current class mentions
    :type mentions_current: list
    :param mentions_previous: list of class mentions last known about
    :type mentions_previous: list
    """
    print(  # I have put the string on it's own line b/c PyCharm's formatter and PEP inspector want different things
            '{id}{_}{author}{_}{title}{_}{action}{_}{mentions_current}{_}{mentions_previous}'
                .format(
                    id = submission_.id,
                    author = submission_.author,
                    title = submission_.title,
                    action = action,
                    mentions_current = mentions_current,
                    mentions_previous = mentions_previous,
                    _ = '\t'))


def post_comment(new_mention_object, actually_do_it = False):
    """Posts a comment on the submission with info about the courses mentioned

    :param new_mention_object:
    :type new_mention_object: PostWithMentions
    :param actually_do_it: whether to actually post a comment to reddit.com
    :type actually_do_it: bool
    :return:
    """
    submission_id = new_mention_object.post_id
    submission_object = reddit.get_submission(submission_id = submission_id)

    mentions_new = new_mention_object.mentions_list

    if submission_id in existing_posts_with_comments.keys():  # already have a comment with class info
        already_commented_obj = existing_posts_with_comments[submission_id]
        mentions_previous = already_commented_obj.mentions_list

        if mentions_new == mentions_previous:  # already have comment, but no new classes have been mentioned
            print_csv_row(submission_object, 'No new mentions.', mentions_new, mentions_previous)
            return

        # comment needs to be updated
        if actually_do_it:
            existing_comment = reddit.get_info(thing_id = 't1_' + already_commented_obj.comment_id)
            existing_comment.edit(_get_comment(db, mentions_new))
            existing_posts_with_comments[submission_id].mentions_list = mentions_new
            _save_posts_with_comments(existing_posts_with_comments)
        print_csv_row(submission_object, 'Edited comment.', mentions_new, mentions_previous)

    else:  # no comment with class info, post a new one
        if actually_do_it:
            new_comment = submission_object.add_comment(_get_comment(db, mentions_new))
            existing_posts_with_comments[submission_id] = ExistingComment(new_comment.id, mentions_new)
            _save_posts_with_comments(existing_posts_with_comments)
        print_csv_row(submission_object, 'Comment added.', mentions_new, [])


def _course_to_markdown(course_):
    """Returns a markdown representation of a course for use in reddit comments. Example:
    '**ECON 1: Into to Stuff**
    >We learn about econ and things.'

    :param course_: Course to get markdown of
    :type course_: Course
    :return: string of markdown of the course
    :rtype: str
    """

    # TODO add the department name?
    # dept_name = dept_names[course_.dept]

    markdown_string = '**{} {}: {}**\n'.format(course_.dept.upper(), course_.number.strip('0'), course_.name)
    markdown_string += '>{}\n\n'.format(course_.description)

    return markdown_string


def _mention_to_course_object(db_, mention_):
    """Converts mention of course to course object

    :param db_: course database with course info
    :type db_: CourseDatabase
    :param mention_: string of course mention, like 'econ 1'
    :type mention_: str
    :return: course database from the mention
    :rtype: Course
    """
    split = mention_.split(' ')

    dept = split[0].lower()
    # if dept == 'cs':
    #     dept = 'cmps'
    # if dept == 'ce':
    #     dept = 'cmpe'

    num = build_database.pad_course_num(split[1].upper())  # eventually get rid of this
    # num = split[1].upper()

    try:
        course_obj = db_.depts[dept].courses[num]
    except KeyError:
        return None

    return course_obj


def _get_comment(db_, mention_list_):
    """Returns a markdown comment with info about the classes mentioned in the list

    :param db_: course database with info
    :type db_: CourseDatabase
    :param mention_list_: list of mentions, like ['econ 1', 'cmps 5j']
    :type mention_list_: list
    :return: string of markdown comment
    :rtype str
    """
    if not mention_list_:  # if list is empty
        return None

    markdown_string = 'Classes mentioned in this thread:\n\n&nbsp;\n\n'

    for mention in mention_list_:
        course_obj = _mention_to_course_object(db_, mention)
        if course_obj is None:  # excepted Keyerror
            continue
        markdown_string += _course_to_markdown(course_obj) + '&nbsp;\n\n'

    markdown_string += '---------------\n\n&nbsp;\n\n' + \
                       '*I am a bot. If I screw up, please comment or message me. ' + \
                       '[I\'m open source!](https://github.com/pfroud/ucsc-class-info-bot)*'

    return markdown_string


def _load_posts_with_comments():
    """Loads from disk the dict of posts that have already been commented on

    :return: dict of ExistingComment objects of posts that have already been commented on
    :rtype: dict
    """
    if not os.path.isfile("pickle/posts_with_comments.pickle"):
        return dict()

    with open("pickle/posts_with_comments.pickle", 'rb') as file:
        a_c = pickle.load(file)
    file.close()
    return a_c


def _save_posts_with_comments(posts_with_comments):
    """Saves to disk the dict of posts that have already been commented on.

    :param posts_with_comments: dict of ExistingComment objects of posts that already have comments on them
    :type posts_with_comments: dict
    """
    with open("pickle/posts_with_comments.pickle", 'wb') as file:
        pickle.dump(posts_with_comments, file)
    file.close()


def _load_found_mentions():
    """Loads from disk the list of found mentions from the last run of find_mentions().

    :return: list of strings of mentions
    :rtype: list
    """
    with open("pickle/found_mentions.pickle", 'rb') as file:
        mentions = pickle.load(file)
    file.close()
    return mentions


db = build_database.load_database()
reddit = tools.auth_reddit()
existing_posts_with_comments = _load_posts_with_comments()  # currently returns empty dict
new_mentions_list = _load_found_mentions()

new_mention = new_mentions_list.pop()
post_comment(new_mention)