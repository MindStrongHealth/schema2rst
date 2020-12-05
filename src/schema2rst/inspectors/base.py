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
import json
from sqlalchemy.engine.reflection import Inspector


class Column(dict):
    def set_comment(self, comment, options=[]):
        extra_comment = ", ".join(options)
        match = re.match('^(.*?)(?:(?:[(（](.*)[)）])|(?:\t(.*)))\s*$', comment)
        if match:
            self['fullname'] = match.group(1).strip()
            self['comment'] = (match.group(2) or match.group(3)).strip()

            if extra_comment:
                self['comment'] += " (%s)" % extra_comment
        elif comment:
            self['fullname'] = comment.strip()
            self['comment'] = extra_comment.strip()
        else:
            self['fullname'] = self['name']
            self['comment'] = extra_comment.strip()


class SimpleInspector(Inspector):
    def __init__(self, bind):
        super(SimpleInspector, self).__init__(bind)

    def get_tables(self, **kw):
        tables = []
        table_names = super(SimpleInspector, self).get_table_names(**kw)
        for table_name in sorted(table_names):
            table = {'name': table_name, 'fullname': ''}
            tables.append(table)

        return tables

    def get_indexes(self, table_name):
        indexes = super(SimpleInspector, self).get_indexes(table_name)
        return sorted(indexes, key=lambda idx: idx['name'])

    def get_foreign_keys(self, table_name):
        fkeys = super(SimpleInspector, self).get_foreign_keys(table_name)
        return sorted(fkeys, key=lambda key: key['name'])

    def get_columns(self, table_name, **kw):
        constraints = self.get_pk_constraint(table_name)
        primary_keys = constraints.get('constrained_columns')
        foreign_keys = self.get_foreign_keys(table_name)
        columns = super(SimpleInspector, self).get_columns(table_name, **kw)

        # wrap column objects in Column class
        columns = [Column(c) for c in columns]

        for column in columns:
            column['fullname'] = column['name']
            column['comment'] = ''

            if column['name'] in primary_keys:
                column['primary_key'] = True
            else:
                column['primary_key'] = False

            column['foreign_keys'] = []
            for key in foreign_keys:
                if column['name'] in key['constrained_columns']:
                    column['foreign_keys'].append(key)

        return columns


    def dump(self):
        ret = dict(name=self.engine.url.database, tables=[])
        print("Getting tables...")
        for table in self.get_tables():
            table_name = table['name']
            print(f"Processing table {table_name}")

            # rename table 'fullname' to 'comment'
            table['comment'] = table['fullname']
            table.pop('fullname',None)

            table['columns'] = []
            table['fields'] = ["name","type","nullable","pkey","default"]
            col_map = {}
            for column in self.get_columns(table_name):
                '''
                .. note::

                    * fullname comes back as the field name when comment is null
                    * fullname is the field's comment if it exists
                    * comment will contain the field's collation as well as any foreign keys

                '''
                metadata = dict(name=column['name'],
                                type=column['type'],
                                nullable=column['nullable'],
                                pkey=column['primary_key'],
                                default=column['default'])

                fk = column['comment']
                if 'FK' not in fk and 'auto_increment' not in fk:
                    pass
                elif 'FK' in fk:
                    # potentially remove collation string
                    metadata['fkey'] = 'FK: ' + fk.split('FK: ', 1)[1]

                    if 'fkey' not in table['fields']:
                        table['fields'].append('fkey')

                if column['fullname'] == column['name']:
                    comment = ''
                else:
                    comment = column['fullname']

                if comment != '' and len(comment):
                    try:
                        comment = json.loads(comment)
                        metadata = {**metadata, **comment}
                        for f in sorted(comment.keys()):
                            if f not in table['fields']:
                                table['fields'].append(f)
                    except json.decoder.JSONDecodeError:
                        metadata["description"] = comment

                        if 'description' not in table['fields']:
                            table['fields'].append('description')

                table['columns'].append(metadata)

            table['indexes'] = []
            for index in self.get_indexes(table_name):
                metadata = dict(name=index['name'],
                                unique=index['unique'],
                                column_names=index['column_names'])
                table['indexes'].append(metadata)

            table['foreign_keys'] = []
            for fkey in self.get_foreign_keys(table_name):

                metadata = dict(name=fkey['name'],
                                constrained_columns=fkey['constrained_columns'],
                                referred_table=fkey['referred_table'],
                                referred_columns=fkey['referred_columns'],
                                )
                table['foreign_keys'].append(metadata)

            ret['tables'].append(table)

        return ret
