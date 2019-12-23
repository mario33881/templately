#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Templately enables you to inject files content
inside a main template file.

Usage:
 templately.py [--ot=<opening_tag>] [--po=<pattern_opening>] [--ct=<closing_tag>]
                     <template> <output> <placeholder=file>...
 templately.py (-h | --help)
 templately.py --version

Options:
 -h --help     Show this screen.
 --version     Show version.


Details:
- <template> is the template file
- <placeholder=file> : * "placeholder" is the string to search inside the template
                       * "file" is a file path of which contents gets injected inside the template
                       > "=" is the char that divides placeholder and the file path
"""

__author__ = "Zenaro Stefano"
__version__ = "01_01 2019-12-21"

import re
from docopt import docopt
import os
import sys

boold = False     # shows/hides debug messages
testmode = False  # shows/hides errors (during unit testing error prints are hidden from the caller)

# pattern variables: default variables say "{{ ty.<?> }}", <?> is the placeholder name
opening_tag = "{{"
pattern_opening = "ty."
closing_tag = "}}"


def re_builder(t_opening_tag, t_pattern_opening, t_closing_tag):

    """Builds the regex pattern string and returns its compiled version.

    The function **escapes t_opening_tag, t_pattern_opening and t_closing_tag**
    using the :func:`re.escape()` function
    and then **concatenates them** into a regex pattern string.

    The **regex string gets compiled** with the :func:`re.compile()` function and is returned by the function.

    Usage example:

    >>> regex_pattern = re_builder("{{", "ty.", "}}")
    >>> print(regex_pattern)
    re.compile('\\{\\{\\s*ty\\.(.*?)\\s*\\}\\}')

    This regex will match the strings that start with `{{ty.` and end with "}}"
    > One or more spaces after "{{" and before "}}" are valid

    :param str t_opening_tag: patterns opening tag
    :param str t_pattern_opening: patterns starting string
    :param str t_closing_tag: patterns closing tag
    :return t_regex_pattern: compiled regex pattern
    :rtype: :class:`_sre.SRE_Pattern`
    """

    if boold:
        print("Internal vars:")
        print("t_opening_tag: '" + t_opening_tag + "'")
        print("t_pattern_opening: '" + t_pattern_opening + "'")
        print("t_closing_tag: '" + t_closing_tag + "'")

    # concatenate escaped t_opening_tag, "\s*" ( num. X of spaces) and escaped t_pattern_opening
    tmp_repattern_opening = re.escape(t_opening_tag) + r"\s*" + re.escape(t_pattern_opening)

    # concatenate "\s*" ( num. X of spaces) and escaped t_closing_tag
    tmp_repattern_closing = r"\s*" + re.escape(t_closing_tag)

    # compile the regex pattern, which is the concatenation of tmp_repattern_opening, "(.*?)" and tmp_repattern_closing
    # > "(.*?)" collects the characters after tmp_repattern_opening and before tmp_repattern_closing
    t_regex_pattern = re.compile(tmp_repattern_opening + r"(.*?)" + tmp_repattern_closing)

    if boold:
        print("t_regex_pattern: '", t_regex_pattern, "'")

    return t_regex_pattern


def get_placeholders(t_fin, t_regex_pattern):

    """Reads the lines of <t_fin> (template file) one by one and returns the placeholders.

    The file is read one line at the time and the regex pattern
    is used to search for the placeholders inside the line

    Example:

    cat template.txt
    this is
    {{ ty.placeholder1 }} a {{ ty.placeholder2 }}
    test {{ ty.placeholder3 }}
    EOF

    >>> get_placeholders(t_fin, '\\{\\{\\s*ty\\.(.*?)\\s*\\}\\}')
    ["placeholder1", "placeholder2", "placeholder3"]

    :param t_fin: template file
    :type t_fin: :class:`_io.TextIO`
    :param t_regex_pattern: regex pattern
    :type t_regex_pattern: :class:`_sre.SRE_Pattern`
    :return t_placeholders: list of template placeholders
    :rtype t_placeholders: list
    """

    # list of the template placeholder
    t_placeholders = []

    # read the first line of the file
    line = t_fin.readline()

    # loop through the file
    while line != "":

        t_placeholders += re.findall(t_regex_pattern, line)

        # read the next line
        line = t_fin.readline()

    return t_placeholders


def equal_vectors(t_v1, t_v2):

    """Checks if the vectors are equal

    The two vectors are copied (to maintain the original values),
    the copies get sorted and a "==" operator checks if these vectors are equal.
    The result of the operator is returned.
    > The vectors have to have the same elements, which means that
    > they also have to have the same number of elements

    :param list t_v1: first list of elements
    :param list t_v2: second list of elements
    :return are_equal: boolean value that indicates if t_v1 and t_v2 are equal
    :rtype are_equal: bool
    """

    # boolean that tells if t_v1 and t_v2 are equal
    are_equal = False

    # the input vectors get copied to maintain their original value
    t_v1_copy = t_v1[:]
    t_v2_copy = t_v2[:]

    try:
        # the vector copies get sorted
        t_v1_copy.sort()
        t_v2_copy.sort()

    except TypeError:
        raise TypeError("Can't sort an array with integers and strings")

    # these vectors are then compared
    if t_v1_copy == t_v2_copy:
        are_equal = True

    return are_equal


def has_duplicates(t_vector):

    """Checks if there are duplicates inside the passed vector

    The function loops for each element inside the vector, the loop
    stops if the vector ends or if a duplicate element is found.

    if one element is present more than one time the vector contains duplicates
    > count() is used to count how many times the element is present inside the vector

    :param list t_vector: list with elements
    :return contains_duplicates: boolean, True if the list t_vector contains duplicates, False otherwise
    :rtype contains_duplicates: bool
    """

    i = 0
    contains_duplicates = False

    # loop for each element inside the vector
    # stop if the vector ends or if a duplicate element is found
    while i < len(t_vector) and not contains_duplicates:

        # if the element is present more than one time, the vector contains duplicates
        if t_vector.count(t_vector[i]) > 1:
            contains_duplicates = True

        i += 1

    return contains_duplicates


def check_input_placeholders(t_placeholders):

    """Makes sure that all the input placeholders are correct

    Specifically it checks if the placeholders contain only one equal sign,
    and if the file paths exist.
    The function returns a dictionary with the check result and the name
    of the placeholders.

    :param list t_placeholders: list of input placeholders
    :return check_result: dictionary with a bool check result and a list with placeholders names
    :rtype check_result: dict
    """

    # dictionary that gets returned by the function
    check_result = {"correct_placeholder": True,  # all the checks are positive
                    "placeholders_names": []      # vector with the placeholder names
                    }

    # check if there is at least one placeholder
    # > this shouldn't happen since docopt requires at least one placeholder, otherwise it shows the help screen,
    # > better be safe than sorry
    if len(t_placeholders) == 0:
        if not testmode:
            print("Bad placeholders: the input doesn't have placeholders", file=sys.stderr)
        check_result["correct_placeholder"] = False

    # loop for each placeholder
    for placeholder in t_placeholders:
        # the placeholder has to have one equal sign
        if placeholder.count("=") == 1:

            # save the placeholder name
            placeholder_name = placeholder.split('=')[0]
            # add it to the vector inside the check_result dict
            check_result["placeholders_names"].append(placeholder_name)

            # save the file path
            file_path = placeholder.split('=')[1]

            # check if the file exists
            if not os.path.isfile(file_path):
                if not testmode:
                    print("File to inject doesn't exist: '" + placeholder + "'", file=sys.stderr)
                check_result["correct_placeholder"] = False
        else:
            if not testmode:
                print("Bad placeholder (use one '=' per placeholder): '" + placeholder + "'", file=sys.stderr)
            check_result["correct_placeholder"] = False

    return check_result


def check_placeholder_arguments(args, t_template_placeholders):

    """Makes sure that every placeholder argument is written in a valid form.

    Specifically it checks :
    - if the input placeholders contain only one equal sign,
    and if the file paths exist with the :func:`check_input_placeholders()` function
    - it makes sure that both the template placeholders and input placeholders have no duplicates
    with the :func:`has_duplicates()` function
    - it makes sure that the template placeholders and input placeholders are equal
    with the :func:`equal_vectors()` function

    :param args: dictionary with input arguments
    :type args: docopt.Dict
    :param list t_template_placeholders: list with the placeholders of the template file
    :return correct_placeholder: boolean value, True if everything is correct, False otherwise
    :rtype correct_placeholder: bool
    """

    # copy the function input, never change the original values
    t_arguments = args

    # check if the input placeholders are correct and get the placeholder names
    check_ip_res = check_input_placeholders(t_arguments['<placeholder=file>'])

    # if this variable is and stays True, the placeholders are correct
    correct_placeholder = check_ip_res["correct_placeholder"]

    # check if the template has at least one placeholder
    # > it shouldn't be a problem: the input placeholders should be at least one
    # > and the template placeholders must be equal to the input placeholder.
    # > This error is more useful to the user than to the script itself
    if len(t_template_placeholders) == 0:
        if not testmode:
            print("Bad placeholders: the template has no placeholders", file=sys.stderr)
        correct_placeholder = False

    # check if the input has placeholder duplicates
    if has_duplicates(check_ip_res["placeholders_names"]):
        if not testmode:
            print("Bad placeholders: the input has placeholders duplicates", file=sys.stderr)
        correct_placeholder = False

    # check if the template has placeholder duplicates
    if has_duplicates(t_template_placeholders):
        if not testmode:
            print("Bad placeholders: the template has duplicates of placeholders", file=sys.stderr)
        correct_placeholder = False

    # check if the template placeholders and the input placeholders are the same
    if not equal_vectors(check_ip_res["placeholders_names"], t_template_placeholders):
        if not testmode:
            print("Bad placeholders: the input and the template placeholders must be the same", file=sys.stderr)
        correct_placeholder = False

    return correct_placeholder


def check_repattern_arguments(args):

    """The function checks if the user passed a specific placeholder pattern and returns the correct configuration.

    The function checks:
    - if the opening tag wasn't specified by the user, if so use the default
    - if the pattern opening wasn't specified by the user, if so use the default
    - if the closing tag wasn't specified by the user, if so use the default

    Example:

    >>> check_repattern_arguments({"--ot": None, "--po": None, "--ct": None})
    {"--ot": "{{", "--po": "ty.", "--ct": "}}"}
    >>> check_repattern_arguments({"--ot": "%%", "--po": "template.", "--ct": "%%"})
    {"--ot": "%%", "--po": "template.", "--ct": "%%"}

    :param dict args: dictionary with the input arguments
    :return t_arguments: dictionary with valid the input argument
    :rtype t_arguments: dict
    """

    # copy the function input, never change the original values
    t_arguments = args

    # if the input doesn't specify an opening tag, use the default one
    if not t_arguments['--ot']:
        t_arguments['--ot'] = opening_tag

    # if the input doesn't specify a pattern opening, use the default one
    if not t_arguments['--po']:
        t_arguments['--po'] = pattern_opening

    # if the input doesn't specify a closing tag, use the default one
    if not t_arguments['--ct']:
        t_arguments['--ct'] = closing_tag

    if boold:
        print("Checked arguments:")
        print(t_arguments)

    return t_arguments


def output_builder(t_fin, t_args, t_regex_pattern):
    """Builds the output file from the template file combined with placeholder files.

    The function opens the output file (we know that the output directory exists),
    then the template file <t_fin> is read one line at a time.

    A regex pattern is used per line to know if it has placeholder(s),
    if it has at least one placeholder an input placeholder is sought
    to get the path of the file to inject into the output.
    > The file to inject is also read one line at a time

    The content of the file is written to the output file and then
    this cycle repeats for all the placeholders of the line.

    If there is no placeholder the line of the template file is directly written to the output.

    Example:

    1. this line is read from the template file
    line = 'this {{ ty.placeholder1 }} is a {{ ty.placeholder2 }} test\\n'

    2. the regex ( '{{ ty.<?> }}' ) finds at least one match, a loop is used to read the first one, the second one, ...

    3. The part before the placeholder is written to the output file

    4. The placeholder ( '<?>', 'placeholder1' ) is sought with another loop inside the input.
    > We already know that the input has a 'placeholder1=<path1>'

    5. The file to inject path is read from the input placeholder (<path1>) and it is used to read that file.
    The content of the file is written inside the output

    6. Phase 3, 4, 5 are repeated until there are placeholders in the line

    7. When all the placeholders have been substituted by the "file to inject" content, the part after
    the last placeholder is written to the output file

    8. The next line of the template file is read and everything repeats itself again

    > If there was no placeholder inside the line, that line is directly written to the output file

    :param t_fin: template file
    :type t_fin: :class:`_io.TextIO`
    :param dict t_args: dictionary with all the input from the terminal
    :param t_regex_pattern: regex pattern
    :type t_regex_pattern: :class:`_sre.SRE_Pattern`
    :return: None
    """

    with open(t_args["<output>"], "w") as fout:
        # read the first line of the file
        line = t_fin.readline()

        # loop through the file
        while line != "":

            # saving the line on another variable that will hold replace() changes
            temp_line = line

            # get an iterator for the matches
            t_placeholders = re.finditer(t_regex_pattern, temp_line)

            # check if at least one match was found
            if any(t_placeholders):

                # set a default value to the suffix
                # > in theory this is useless, the suffix will always have a value before the fout.write(suffix)
                # > but "better be safe than sorry"
                suffix = ""

                # loop for each element in the iterator
                # > for placeholder in placeholders doesn't work for more than one placeholder per line
                for placeholder in re.finditer(t_regex_pattern, temp_line):

                    # from the regex get the group with the part of string to substitute
                    # examples use the default pattern: {{ ty.<?> }}
                    tosub = placeholder.group(0)  # example: '{{ ty.<?> }}'

                    # from the regex get the group with the name of the placeholder
                    placeholder_name = placeholder.group(1)  # example: '<?>'

                    # divide line into 3 parts:
                    # the part before the separator, the separator itself, and the part after the separator
                    prefix, sep, suffix = temp_line.partition(tosub)

                    # write the part of the template line before the placeholder
                    fout.write(prefix)

                    found_placeholder = False  # the placeholder was found in the arguments
                    i = 0  # temporary variable

                    # loop for each placeholder input
                    # > the loop stops when a placeholder was found or if the full array was read
                    # > (this should be impossible, we made sure that the placeholder exists during the script exec)
                    while not found_placeholder and i < len(t_args["<placeholder=file>"]):
                        # save the input placeholder
                        input_placeholder = t_args["<placeholder=file>"][i]

                        # if the input placeholder has the name of the placeholder in the template file
                        if input_placeholder.split("=")[0] == placeholder_name:
                            # get the path of the file to inject
                            file_path = input_placeholder.split("=")[1]

                            # open it
                            with open(file_path, "r") as fpo:
                                # read the first line
                                fpo_line = fpo.readline()

                                # read the file one line at a time
                                while fpo_line != "":
                                    # write the line of the file to inject inside the output file
                                    fout.write(fpo_line)

                                    # read the next file
                                    fpo_line = fpo.readline()

                            # the placeholder was found, stop the loop
                            found_placeholder = True

                        i += 1

                    # modify the temporary variable with the line,
                    # the part before the placeholder and the placeholder itself are deleted from the line
                    # > this is useful when two or more placeholders are on the same line because the prefix
                    # > of the second, third ... placeholder would have the previous placeholder in it
                    temp_line = temp_line.replace(prefix + tosub, "")

                # write the part of the template line after the placeholder
                fout.write(suffix)

            else:
                # no matches/placeholders were found, the whole line gets written to the output
                fout.write(temp_line)

            # read the next line
            line = t_fin.readline()


if __name__ == "__main__":

    if boold:
        print("Start")
        print("-" * 50)

    # get from the scripts docstring the possible arguments and collect them from the user
    arguments = docopt(__doc__, version=__version__)

    if boold:
        print("Arguments:")
        print(arguments)

    # if the template file doesn't exist, output as a standard error and exit with status 1
    if not os.path.isfile(arguments['<template>']):
        print("Template file not found! (or it wasn't a file)", file=sys.stderr)
        sys.exit(1)

    # save the output directory path
    output_path = os.path.dirname(os.path.abspath(arguments['<output>']))

    # check if the output dir doesn't exist, if so exit with status 3
    if not os.path.isdir(output_path):
        print("The output folder doesn't exist!", file=sys.stderr)
        sys.exit(3)

    # open the template file
    with open(arguments['<template>'], 'r') as fin:

        # check if some of the regex pattern arguments have been passed
        c_re_args = check_repattern_arguments(arguments)

        # get the regex of the placeholders pattern
        regex_pattern = re_builder(c_re_args['--ot'], c_re_args['--po'], c_re_args['--ct'])

        # get the placeholders of the template file
        placeholders = get_placeholders(fin, regex_pattern)

        if boold:
            print("placeholders")
            print(placeholders)

        # check that all the arguments are correct
        corr_placeholder = check_placeholder_arguments(c_re_args, placeholders)

        # if at least one of the placeholders are incorrect, exit with status 2
        if not corr_placeholder:
            sys.exit(2)

        # now that all the checks have been made, go back to the start of the file
        fin.seek(0)

        # build the output file
        output_builder(fin, c_re_args, regex_pattern)

    if boold:
        print("-" * 50)
        print("Stop")
