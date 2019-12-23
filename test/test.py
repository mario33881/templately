#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Templately test file"""

import os
import sys
import re
import unittest

# add to the python path the folder with templately
test_path = os.path.dirname(sys.argv[0])
templately_path = os.path.join(test_path, "..", "templately")
sys.path.insert(0, os.path.abspath(templately_path))

# importing templately to test it
import templately  # noqa: E402

# hide error prints from the caller
templately.testmode = True


class TestTemplately(unittest.TestCase):

    def test_re_builder(self):
        """
        Tests re_builder(t_opening_tag, t_pattern_opening, t_closing_tag) function

        The tested function:
        Builds the regex pattern string and returns its compiled version.

        Usage example:

        >>> regex_pattern = re_builder("{{", "ty.", "}}")
        >>> print(regex_pattern)
        re.compile('\\{\\{\\s*ty\\.(.*?)\\s*\\}\\}')
        """

        # define variables for testing
        t_default_opening_tag = "{{"
        t_default_pattern_opening = "ty."
        t_default_closing_tag = "}}"

        t_custom_opening_tag = "%%"
        t_custom_pattern_opening = "template."
        t_custom_closing_tag = "$$"

        # passing the default
        default_re = templately.re_builder(t_default_opening_tag, t_default_pattern_opening, t_default_closing_tag)
        self.assertEqual(default_re, re.compile('\\{\\{\\s*ty\\.(.*?)\\s*\\}\\}'))

        # passing all custom parameters
        custom_re = templately.re_builder(t_custom_opening_tag, t_custom_pattern_opening, t_custom_closing_tag)
        self.assertEqual(custom_re, re.compile('\\%\\%\\s*template\\.(.*?)\\s*\\$\\$'))

    def test_get_placeholders(self):
        """
        Tests get_placeholders(t_fin, t_) function

        Reads the lines of <t_fin> (template file) one by one and returns the placeholders.

        Example:

        cat template.txt
        this is
        {{ ty.placeholder1 }} a {{ ty.placeholder2 }}
        test {{ ty.placeholder3 }}
        EOF

        >>> get_placeholders(t_fin)  # t_fin is the template.txt open file
        ["placeholder1", "placeholder2", "placeholder3"]
        """

        with open(os.path.join(test_path, "template.txt"), "r") as f:
            placeholders = templately.get_placeholders(f, '\\{\\{\\s*ty\\.(.*?)\\s*\\}\\}')

        self.assertEqual(placeholders, ["placeholder1", "placeholder2", "placeholder3"])

    def test_equal_vectors(self):
        """
        Tests equal_vectors(t_v1, t_v2) function

        Checks if the vectors are equal
        """

        # test empty vectors, should be True
        self.assertTrue(templately.equal_vectors([], []))

        # test equal vectors but with different types inside, raises TypeError
        v1 = [1, "2", {"test": []}]
        v2 = ["2", 1, {"test": []}]

        with self.assertRaises(TypeError):
            templately.equal_vectors(v1, v2)

        # test slightly different vectors, sould be False
        v1 = ["2", "1"]
        v2 = ["2", "1", "3"]
        self.assertFalse(templately.equal_vectors(v1, v2))

        # test empty vector with vector with elements, should be False
        v1 = []
        v2 = [2, 3, 1]
        self.assertFalse(templately.equal_vectors(v1, v2))

        # test vector containing 0 with empty vector, should be False
        v1 = [0]
        v2 = []
        self.assertFalse(templately.equal_vectors(v1, v2))

        # test vector containing empty vector and an empty vector, should be False
        v1 = []
        v2 = [[]]
        self.assertFalse(templately.equal_vectors(v1, v2))

    def test_has_duplicates(self):
        """
        Tests has_duplicates(t_vector) function

        Checks if there are duplicates inside the passed vector
        """
        # test empty vectors, should be False
        self.assertFalse(templately.has_duplicates([]))

        # test vector with one element, should be False
        self.assertFalse(templately.has_duplicates([1]))

        # test vector with equal elements, should be True
        self.assertTrue(templately.has_duplicates(["0", "0"]))

        # test vector with different elements, should be False
        self.assertFalse(templately.has_duplicates(["1", 1]))

    def test_check_input_placeholders(self):
        """
        Tests check_input_placeholders(t_placeholders) function

        Makes sure that all the input placeholders are correct
        """

        # test empty vector, return should be {"correct_placeholder": False, "placeholders_names": []}
        check_result = templately.check_input_placeholders([])
        self.assertEqual(check_result, {"correct_placeholder": False, "placeholders_names": []})

        # test vector with only the placeholder name, no "=", no file path to inject
        check_result = templately.check_input_placeholders(["a"])
        self.assertEqual(check_result, {"correct_placeholder": False, "placeholders_names": []})

        # test vector with "=", no placeholder name, no file path to inject
        check_result = templately.check_input_placeholders(["="])
        self.assertEqual(check_result, {"correct_placeholder": False, "placeholders_names": [""]})

        # test vector with "." as path
        check_result = templately.check_input_placeholders(["a=."])
        self.assertEqual(check_result, {"correct_placeholder": False, "placeholders_names": ["a"]})

        # test vector with file path that doesn't exist
        check_result = templately.check_input_placeholders(["a=totallynotexistent.file"])
        self.assertEqual(check_result, {"correct_placeholder": False, "placeholders_names": ["a"]})

        # test to file that does exist
        check_result = templately.check_input_placeholders(["a=" + os.path.join(test_path, "file1.txt")])
        self.assertEqual(check_result, {"correct_placeholder": True, "placeholders_names": ["a"]})

    def test_check_placeholder_arguments(self):
        """
        Tests check_placeholder_arguments(args, t_template_placeholders) function

        Makes sure that every placeholder argument is written in a valid form.

        Specifically it checks :
        - if the input placeholders contain only one equal sign,
        and if the file paths exist with the :func:`check_input_placeholders()` function
        - it makes sure that both the template placeholders and input placeholders have no duplicates
        with the :func:`has_duplicates()` function
        - it makes sure that the template placeholders and input placeholders are equal
        with the :func:`equal_vectors()` function
        """
        # test empty vectors, return should be False
        check_result = templately.check_placeholder_arguments({'<placeholder=file>': []}, [])
        self.assertFalse(check_result)

        # test vector input vector with only the placeholder name, no "=", no file path to inject.
        # empty template placeholders vector
        check_result = templately.check_placeholder_arguments({'<placeholder=file>': ["a"]}, [])
        self.assertFalse(check_result)

        # test vector with "=", no placeholder name, no file path to inject
        # empty template placeholders vector
        check_result = templately.check_placeholder_arguments({'<placeholder=file>': ["="]}, [])
        self.assertFalse(check_result)

        # test vector with "." as path
        # empty template placeholders vector
        check_result = templately.check_placeholder_arguments({'<placeholder=file>': ["a=."]}, [])
        self.assertFalse(check_result)

        # test vector with file path that doesn't exist
        # empty template placeholders vector
        check_result = templately.check_placeholder_arguments({'<placeholder=file>': ["a=totallynotexistent.file"]}, [])
        self.assertFalse(check_result)

        # test to file that does exist
        # empty template placeholders vector
        check_result = templately.check_placeholder_arguments({'<placeholder=file>': ["a=file1.txt"]}, [])
        self.assertFalse(check_result)

        # test with duplicates in the input vector
        check_result = templately.check_placeholder_arguments({'<placeholder=file>': ["a=file1.txt", "a=file1.txt"]},
                                                              [""])
        self.assertFalse(check_result)

        # test with duplicates in the input vector
        check_result = templately.check_placeholder_arguments({'<placeholder=file>': ["a=file1.txt"]}, ["a", "a"])
        self.assertFalse(check_result)

        # test with more elements in the input placeholders
        check_result = templately.check_placeholder_arguments({'<placeholder=file>': ["a=file1.txt", "b=file1.txt"]},
                                                              ["a"])
        self.assertFalse(check_result)

        # test with more elements in the template placeholders
        check_result = templately.check_placeholder_arguments({'<placeholder=file>': ["a=file1.txt"]}, ["a", "b"])
        self.assertFalse(check_result)

        # test with different placeholders
        check_result = templately.check_placeholder_arguments({'<placeholder=file>': ["b=file1.txt", "a=file1.txt"]},
                                                              ["a", "c"])
        self.assertFalse(check_result)

        # test with the same placeholders
        check_result = templately.check_placeholder_arguments({'<placeholder=file>': ["b=" + os.path.join(test_path,
                                                                                                          "file1.txt"),
                                                                                      "a=" + os.path.join(test_path,
                                                                                                          "file1.txt")
                                                                                      ]
                                                               },
                                                              ["a", "b"])
        self.assertTrue(check_result)

    def test_check_repattern_arguments(self):
        """
        Tests check_repattern_arguments(args) function

        The function checks if the user passed a specific placeholder pattern and returns the correct configuration.
        """
        # define variables for testing
        t_default_opening_tag = "{{"
        t_default_pattern_opening = "ty."
        t_default_closing_tag = "}}"

        t_custom_opening_tag = "%%"
        t_custom_pattern_opening = "template."
        t_custom_closing_tag = "$$"

        # passing None, returns defaults
        args = templately.check_repattern_arguments({"--ot": None, "--po": None, "--ct": None})
        self.assertEqual(args, {"--ot": "{{", "--po": "ty.", "--ct": "}}"})

        # passing defaults
        args = templately.check_repattern_arguments({"--ot": t_default_opening_tag, "--po": t_default_pattern_opening,
                                                     "--ct": t_default_closing_tag})
        self.assertEqual(args, {"--ot": "{{", "--po": "ty.", "--ct": "}}"})

        # passing all custom parameters
        args = templately.check_repattern_arguments({"--ot": t_custom_opening_tag, "--po": t_custom_pattern_opening,
                                                     "--ct": t_custom_closing_tag})
        self.assertEqual(args, {"--ot": "%%", "--po": "template.", "--ct": "$$"})

        # passing mixed parameters
        args = templately.check_repattern_arguments({"--ot": None, "--po": t_default_pattern_opening,
                                                     "--ct": t_custom_closing_tag})
        self.assertEqual(args, {"--ot": "{{", "--po": "ty.", "--ct": "$$"})

    def test_output_builder(self):
        """
        Tests output_builder(t_fin, t_args) function

        Builds the output file from the template file combined with placeholder files.
        """

        expected_output = "this is\n----\nthis\nis placeholder1\ncontent\n---- a ----\nthis\nis placeholder2\n" \
                          "content\n----\ntest ----\nthis\nis placeholder3\ncontent\n----"

        with open(os.path.join(test_path, "template.txt"), "r") as t_fin:
            templately.output_builder(t_fin,
                                      {"<output>": os.path.join(test_path, "output.txt"),
                                       '<placeholder=file>': ["placeholder1=" + os.path.join(test_path, "file1.txt"),
                                                              "placeholder2=" + os.path.join(test_path, "file2.txt"),
                                                              "placeholder3=" + os.path.join(test_path, "file3.txt")
                                                              ]
                                       },
                                      re.compile('\\{\\{\\s*ty\\.(.*?)\\s*\\}\\}'))

        with open(os.path.join(test_path, "output.txt"), "r") as fout:
            are_equal = False
            text = fout.read()
            if text == expected_output:
                are_equal = True

        self.assertTrue(are_equal)


if __name__ == "__main__":
    # start unit tests
    unittest.main()
