SQL Parser
================

A utility to parse column and table relations referenced out of a SQL statement.

Highly influenced by https://github.com/macbre/sql-metadata, but designed for more analytics-y queries with lots of CTEs, subqueries, window functions, and other complexity.

Usage:

Install:

```sh
pip install git+https://github.com/wrgoldstein/sql-metaparse
```

Use:

```python
import sql_metaparse

q = """
select * from foo
"""

sql_metaparse.parse_meta(q)['tables']  # ['"foo"']
```

Or sometimes it's more convenient on the command line:

```sh
pbpaste | python -c "import sys; import sql_metaparse as sm; print(sm.parse_meta(sys.stdin)['tables'])"
```
