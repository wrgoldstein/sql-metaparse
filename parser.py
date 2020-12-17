import sqlparse
from itertools import dropwhile
from functools import partial
from typing import List
# in the middle of fixing up columns and comments to be nice to parse

sformat = partial(sqlparse.format, reindent=True, keyword_case='lower')

Whitespace = sqlparse.tokens.Whitespace
Punctuation = sqlparse.tokens.Punctuation
Keyword = sqlparse.tokens.Keyword
Name = sqlparse.tokens.Name
Comment = sqlparse.tokens.Comment.Single
Symbol = sqlparse.tokens.Literal.String.Symbol
CTE = sqlparse.tokens.CTE
DML = sqlparse.tokens.DML


def take_name(tokens: list) -> tuple:
    n = len(tokens)
    if not n or tokens[0].ttype not in [Name, Symbol]:
        return None, tokens
    if n < 3 or tokens[1].ttype != Punctuation or tokens[1].value != '.' or tokens[2].ttype not in [Name, Symbol]:
        return normalize_names(tokens[0]), tokens[1:]
    return normalize_names(tokens[0], tokens[2]), tokens[3:]

def normalize_names(*tokens):
    return ".".join([f'"{token.value}"' if token.ttype == Name else token.value for token in tokens])

def normalize_string_names(*strings):
    return ".".join([f'"{s}"' if not (s.startswith('"') and s.endswith('"')) else s for s in strings])

def ending_token(token):
    # if we find any of these tokens, we stop assuming we're in the context
    # of a `from` clause.
    if token.is_keyword and token.normalized in ["ON", "WHERE", "LIMIT", "GROUP", "SELECT"]:
        return True
    elif token.value in ("(", ")"):
        return True
    return False


def beginning_token(token):
    keywords = "FROM", "LEFT JOIN", "RIGHT JOIN", "INNER JOIN", "OUTER JOIN", "FULL OUTER JOIN"
    if token.is_keyword and token.normalized in keywords:
        return True
    else:
        return False


def find_tables_used_from_tokens(tokens: list):
    in_from = False
    while len(tokens) > 0:
        if not in_from:
            first, *tokens = tokens
            if beginning_token(first):
                in_from = True  # Start actively looking for Name tokens
                continue

        else:
            if ending_token(tokens[0]):
                in_from = False
                continue
            name, tokens = take_name(tokens)
            
            if name is None:
                # Didn't find a name, so just keep going
                first, *tokens = tokens
            else:
                yield name
                # found a table name, make sure to remove any alias
                tokens = list(dropwhile(lambda t: t.ttype == Whitespace or t.ttype == Name or t.ttype == Symbol, tokens))

def search_for_top_level_select(tokens):
    nesting = []
    while len(tokens) > 0:
        token, *tokens = tokens
        if token.value == "(":
            nesting.append("(")
        elif token.value == ")":
            if nesting[-1] == "(":
                nesting.pop()
            else:
                raise Exception("Encountered unmatched parentheses")
        if token.value == "case":
            nesting.append("case")
        elif token.value == "end":
            if nesting[-1] == "case":
                nesting.pop()
            else:
                raise Exception("Encountered unmatched case statement")
        
        if not len(nesting) and token.ttype == DML:
            # This is where top level select statements start
            return tokens

def _clean_column(column: tuple):
    """
    
    """
    column_parts, comment_parts = column
    name = column_parts[-1]
    column = sformat(" ".join(column_parts))
    comment_parts = [ s.lstrip("-").strip() for s in comment_parts]
    comments = "\n".join(comment_parts).strip() or None
    return column, name, comments


def parse_columns(tokens: List[sqlparse.tokens._TokenType]) -> List[tuple]:
    """
    Parse a list of top level columns selected along with 
    any comments made.
    """
    tokens = list(tokens.flatten())
    tokens = search_for_top_level_select(tokens)
    tokens = list(dropwhile(lambda t: t.ttype == Whitespace, tokens))
    columns = []
    current_column = []
    current_comments = []
    while len(tokens) > 0:
        token, *tokens = tokens

        if token.ttype in [Keyword, Name, Symbol]:
            current_column.append(token.value)
        elif token.ttype == Comment:
            current_comments.append(token.value)
        elif token.normalized == 'FROM' or token.value == ",":
            # done with this column
            columns.append((current_column, current_comments))
            current_column = []
            current_comments = []
    if current_column:
        columns.append((current_column, current_comments))
    columns = list(map(_clean_column, columns))
    return columns

def parse_tables(tokens: List[sqlparse.tokens._TokenType]) -> List[str]:
    ctes = []
    if tokens.token_first().ttype == CTE:
        sublists = tokens.get_sublists()
        ctes = list(filter(None.__ne__, [x.get_name() for x in sublists]))
        ctes = normalize_string_names(*ctes)

    tokens = list(tokens.flatten())
    naive_tables = list(find_tables_used_from_tokens(tokens))
    # Remove any CTE table names since these are not
    # true tables.
    tables = [x for x in naive_tables if x not in ctes]
    return tables


def parse_meta(sql: str) -> dict:

    parsed = sqlparse.parse(sql)[0]
    tables = parse_tables(parsed)
    columns = parse_columns(parsed)

    return dict(columns=columns, tables=tables)

