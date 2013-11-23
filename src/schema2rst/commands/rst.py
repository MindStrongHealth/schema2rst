# -*- coding: utf-8 -*-

import io
import sys
import six
import yaml
import optparse
from schema2rst import inspectors
from schema2rst.rst import RestructuredTextGenerator


def parse_option(args):
    usage = 'Usage: schema2rst CONFIG_FILE'
    parser = optparse.OptionParser(usage=usage)
    parser.add_option('-o', '--output', action='store')

    options, args = parser.parse_args(args)
    if len(args) != 1:
        parser.print_usage()
        sys.exit(0)

    return options, args


def main(args=sys.argv[1:]):
    options, args = parse_option(args)

    config = yaml.load(io.open(args[0], encoding='utf-8'))
    insp = inspectors.create_for(config)

    doc = RestructuredTextGenerator(options.output)
    doc.header(six.u('Schema: %s' % config['db']))

    for table in insp.get_tables():
        # FIXME: support fullname (table comment)
        if table['fullname']:
            doc.header(six.u("%s (%s)") %
                       (table['fullname'], table['name']), '-')
        else:
            doc.header(table['name'], '-')

        headers = ['Fullname', 'Name', 'Type', 'NOT NULL',
                   'PKey', 'Default', 'Comment']
        doc.listtable(headers)

        for c in insp.get_columns(table['name']):
            columns = [c.get('fullname'), c.get('name'), c.get('type'),
                       c.get('nullable'), c.get('primary_key'),
                       c.get('default'), c.get('comment')]
            doc.listtable_column(columns)

        indexes = insp.get_indexes(table['name'])
        if indexes:
            doc.header(six.u('Keys'), '^')
            for index in indexes:
                if index['unique']:
                    format = six.u("UNIQUE KEY: %s (%s)")
                else:
                    format = six.u("KEY: %s (%s)")

                string = format % (index['name'],
                                   ', '.join(index['column_names']))
                doc.list_item(string)