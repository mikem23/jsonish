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

    [ hello world ]
    [ hello    world ]
    [ "hello world" ]

Special characters (like `,`) are not included in the bare word.

    [ hello, world ]
    [ "hello",  "world" ]

Bare words are allowed in array keys too

    {a:1, b:2}
    {"a":1, "b":2}

Bare words cannot contain any special characters (`{}[]:,#'"`), whitespace, or
escaped characters. For such values, use a quoted string.

Adjacent bare words are joined with a space, as are bare words adjacent to
quoted strings.


implicit string joins
---------------------

Much like in Python, two adjacent string values are implicitly joined. This
is done with no separator if both are quoted strings. If either string is
a bare word, then the values are joined with a space.


    [ I "like " 'traffic' lights ]
    [ "I like traffic lights" ]


comments
--------

The hash character (`#`) marks the start of a comment, which continues until
the end of line. All characters in comments are ignored.

    {   name: Arthur,
        title: King of the Britons  # well, I didn't vote for him
        # (you don't vote for kings)
        address: Camelot,  # it's only a modeel
        quest: To seek the Holy Grail,  # or at least a grail shaped beaon
    }
    
    {"name": "Arthur", "title": "King of the Britons", "address": "Camelot",
        "quest": "To seek the Holy Grail"}


single quoted strings
---------------------

Quoted strings may use either single or double quotes, as long as they match.
Either quotation mark may be escaped in strings, regardless of the quote used.
