# -*- coding: utf-8 -*-
#  Copyright 2011 Takeshi KOMIYA
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import io
import re
import six
import sys
import unicodedata


def string_width(string):
    width = 0
    for c in string:
        try:
            char_width = unicodedata.east_asian_width(c)
            if char_width in "WFA":
                width += 2
            else:
                width += 1
        except TypeError:
            width += 1

    return width


class RestructuredTextWriter:
    def __init__(self, filename=None):
        if filename:
            self.stream = io.open(filename, 'w', encoding='utf-8')
        else:
            self.stream = io.open(sys.stdout.fileno(), 'w', encoding='utf-8')

    @staticmethod
    def conform_name(n):
        """Escape trailing underscores for sphinx

        Sphinx treates a trailing underscore as a hyperlink; some fields
        or table names my have a trailing underscore. This escapes that
        underscore so it doesn't hyperlink.

        NOTE: this, as a consequence, will escape all hyperlinks. TOFIX
        """
        if type(n) == str:
            return re.sub(r"([_]+)$", r'\\\1', n)
        else:
            return n

    def close(self):
        self.stream.close()

    def println(self, string):
        self.stream.write(string + six.u("\n"))

    def title(self, title, char="="):

        self.println("")
        self.println(title)
        self.println(char * string_width(title))
        self.println("")

    def header(self, schema, table, comment, char="="):
        """Table header"""

        header = f"{schema}.{table}"

        table = self.conform_name(table)
        ref = f".. _{header}:"

        self.println("")
        self.println(ref)
        self.println("")
        self.println(header)
        self.println(char * string_width(header))
        self.println("")

        if comment != '':
            self.println(comment)
            self.println("")

    def listtable(self, header=None):
        self.println(".. list-table::")
        if header:
            self.println("   :header-rows: 1")

        self.println("")

        if header:
            self.listtable_column(header)

    def listtable_column(self, columns):
        for i, column in enumerate(columns):
            column = self.conform_name(column)
            if i == 0:
                self.println("   * - %s" % column)
            else:
                self.println("     - %s" % column)

    def list_item(self, item):
        self.println("* %s" % item)

    def toctree(self, items, options=[]):
        self.println(".. toctree::")

        for option in options:
            self.println(f"   {option}")

        self.println("")
        for item in items:
            self.println(f"   {item}")

