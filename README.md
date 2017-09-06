jsonish
=======

This is a toy project in early development.

This library provides an extended json parser that supports some syntax
conveniences, such as:

  * bare words
  * implicit string joins
  * comments
  * single quotes for strings


bare words
----------

Bare words are allowed in place of quoted strings. For example the following
syntax pairs are equivalent:

    >>> jsonish.parse(r'[ hello    world ]')
    [u'hello world']

Special characters (like `,`) are not included in the bare word.

    >>> jsonish.parse(r'[ hello, world ]')
    [u'hello', u'world']

Bare words are allowed in array keys too

    >>> jsonish.parse(r'{a:1, b:2}')
    {u'a': 1, u'b': 2}

Bare words cannot contain any special characters (`{}[]:,#'"`), whitespace, or
escaped characters. For such values, use a quoted string.

Also, bare words may not begin with a digit. This prevents poorly formatted
numbers from being parsed as a bare word. For such values, use a quoted string.

    >>> jsonish.parse(r'[ 00hi ]')
    ValueError: Strings beginning with numbers must be quoted

Adjacent bare words are joined with a space, as are bare words adjacent to
quoted strings.


implicit string joins
---------------------

Much like in Python, two adjacent string values are implicitly joined. This
is done with no separator if both are quoted strings. If either string is
a bare word, then the values are joined with a space.

    >>> jsonish.parse(r''' [ I "like " 'traffic' lights ]  ''')
    [u'I like traffic lights']


comments
--------

The hash character (`#`) marks the start of a comment, which continues until
the end of line. All characters in comments are ignored.

>>> jsonish.parse(r'''
... {   name: Arthur,
...     title: King of the Britons,  # well, I didn't vote for him
...     address: Camelot,  # it's only a model
...     quest: To seek the Holy Grail,
... } ''')
{u'quest': u'To seek the Holy Grail', u'address': u'Camelot', u'name': u'Arthur', u'title': u'King of the Britons'}


single quoted strings
---------------------

Quoted strings may use either single or double quotes, as long as they match.
Either quotation mark may be escaped in strings, regardless of the quote used.

    >>> jsonish.parse(r''' 'hello' ''')
    u'hello'
    >>> jsonish.parse(r''' "hello" ''')
    u'hello'


other conveniences
------------------

  * trailing commas are allowed in lists and dictionaries
  * accepts broader numeric formats
  * control characters allowed in strings
