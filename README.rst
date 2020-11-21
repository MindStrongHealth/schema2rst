`schema2rst` generates reST doc from database schema

Features
========
Generates table definitions document from database schema.
`schema2rst` recognizes your database comments on tables and columns,
and reflect it to docs.

Setup
=====

Use easy_install (or pip):

   $ sudo easy_install schema2rst

Configuration
=============
Make config.yaml to connect your database server.
This is example for MySQL Server::

   type: mysql
   db: sample
   host: localhost
   user: username
   passwd: passw0rd
   port: 3306

`type` parameter is accept these values: mysql, mysql+pymysql, postgresql

Usage
=====
Execute schema2rst command writing entire schema to a single RST::

   $ schema2rst -c config.yaml -o database.rst

Execute schema2rst command writing each table of schema to individual RST::

   $ schema2rst -c config.yaml

Examples
========

You can see example at http://tk0miya.bitbucket.org/schema2rst/build/html/ .


Requirements
============
* Python 2.6, 2.7, 3.2, 3.3, 3.4
* SQLAlchemy
* PyYAML
* Six
* pymysql or MySQL-python (optional)
* psycopg2 (optional)

License
=======
Apache License 2.0
