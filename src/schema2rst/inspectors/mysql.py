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

import re
from schema2rst.inspectors import common


class Inspector(common.Inspector):
    def get_tables(self, **kw):
        tables = super(Inspector, self).get_tables(**kw)
        for table in tables:
            query = ("""SELECT TABLE_COMMENT
                        FROM information_schema.Tables
                        WHERE TABLE_SCHEMA = '%s' AND TABLE_NAME = '%s'""" %
                     (self.default_schema_name, table['name']))
            r = self.bind.execute(query).fetchone()

            table['fullname'] = re.sub('; InnoDB.*$', '', r[0])
            if table['fullname'].startswith('InnoDB'):
                table['fullname'] = None

        return tables

    def get_foreign_keys_for_column(self, table_name, column_name, *kw):
        fk = self.get_foreign_keys(table_name, *kw)
        return [k for k in fk if column_name in k['constrained_columns']]

    def get_columns(self, table_name, **kw):
        columns = super(Inspector, self).get_columns(table_name, **kw)
        for column in columns:
            query = ("""SELECT COLUMN_TYPE, COLLATION_NAME,
                               EXTRA, COLUMN_COMMENT
                        FROM information_schema.Columns
                        WHERE TABLE_SCHEMA = '%s' AND TABLE_NAME = '%s' AND
                              COLUMN_NAME = '%s'""" %
                     (self.default_schema_name, table_name, column['name']))
            r = self.bind.execute(query).fetchone()
            column['type'] = r[0]

            options = []
            collation_name = r[1]
            if collation_name and collation_name != 'utf8_general_ci':
                options.append(collation_name)

            extra = r[2]
            if extra:
                options.append(extra)

            fk = self.get_foreign_keys_for_column(table_name, column['name'])
            if fk:
                for key in fk:
                    for refcolumn in key['referred_columns']:
                        msg = "FK: %s.%s" % (key['referred_table'], refcolumn)
                        options.append(msg)

            comment = r[3]
            extra_comment = ", ".join(options)
            match = re.match('^(.*?)(?:\(|（)(.*)(?:\)|）)\s*$', comment)
            if match:
                column['fullname'] = match.group(1).strip()
                column['comment'] = match.group(2).strip()

                if extra_comment:
                    column['comment'] += " (%s)" % extra_comment
            elif comment:
                column['fullname'] = comment.strip()
                column['comment'] = extra_comment.strip()
            else:
                column['fullname'] = column['name']
                column['comment'] = extra_comment.strip()

        return columns
