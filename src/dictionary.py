# -*- coding: utf-8 -*-
"""Requests the definition of a word and outputs it.

Word lookups are made using a free dictionary API. If the word is not found, it's
assumed to be misspelled, and autocorrect will be attempted.
"""

import argparse
import json
import textwrap
import urllib.parse
import urllib.request

from spell import SpellChecker


def request_word(word):
    """Makes a URL request for the specified word

    Args:
        word (str): The word to request

    Returns:
        (response | None): The decoded response (if any). Data is returned in the following format:
            [
                {
                "word":"data",
                "meanings":
                    [
                        {
                        "partOfSpeech":"noun",
                        "definitions":
                            [
                                {
                                "definition":"facts and statistics collected together for reference or analysis.",
                                "synonyms":["facts","figures","statistics","details","particulars","specifics","features","information","evidence","intelligence","material","background","input","proof","fuel","ammunition","statement","report","return","dossier","file","documentation","archive(s)","info","dope","low-down","deets","gen"],
                                }
                            ]
                        }
                    ]
                },
            ]
    """
    sanitized_word = urllib.parse.quote(word)
    url = 'https://api.dictionaryapi.dev/api/v2/entries/en/{}'.format(sanitized_word)

    try:
        with urllib.request.urlopen(url) as page:
            response = json.loads(page.read().decode())
    except urllib.error.HTTPError:
        response = None

    return response


def format_response(response):
    """Displays the retrieved word data.

    Args:
        data (list): Word data response to display

    Returns:
        string: The formatted definition(s)
    """
    # Number of characters to wrap text at
    OUTPUT_WIDTH = 80

    output = ''

    for word in response:
        text_title = word['word'].title()
        output += '\n\n'
        output += '=' * OUTPUT_WIDTH
        output += '\n{}'.format(text_title)

        definition_number = 1

        for meaning in word['meanings']:
            for definition in meaning['definitions']:
                # Get part of speech if present
                text_part_of_speech = ''
                if 'partOfSpeech' in meaning:
                    text_part_of_speech = '({}): '.format(meaning['partOfSpeech'].title())

                # Ensure definition is present
                if 'definition' not in definition:
                    continue

                # Output definition line
                text_definition = '{}. {}{}'.format(
                    definition_number, text_part_of_speech, definition['definition'])
                output += '\n\n'
                output += textwrap.fill(text_definition, width=OUTPUT_WIDTH,
                                        subsequent_indent='   ')

                # Get synonyms if present
                text_synonyms = None
                if 'synonyms' in definition and len(definition['synonyms']) > 0:
                    syn_indent = '      '

                    # Output synonym line

                    output += '\n\n{}Synonyms:\n'.format(syn_indent)
                    text_synonyms = ', '.join(definition['synonyms'])
                    output += textwrap.fill(text_synonyms, width=OUTPUT_WIDTH,
                                            initial_indent=syn_indent, subsequent_indent=syn_indent)

                definition_number += 1

    return output


def lookup_word(word):
    """Look up the specified word. If nothing is found autocorrect is performed

    Args:
        word (str): The word to look up
    """
    output = ''

    # Request the word
    response = request_word(word)
    if response is None:

        # Attempt to correct the input word for misspellings
        checker = SpellChecker()
        corrected = checker.correction(word)

        if corrected == word:
            output += 'Couldn\'t find a definition for \'{}\', I\'m not sure what you meant.'.format(
                word)
        else:
            output += 'Couldn\'t find a definition for \'{}\', you must\'ve meant \'{}\'.'.format(
                word, corrected)
            response = request_word(corrected)

    # Display the response (if any)
    if response is not None:
        output += format_response(response)

    return output


def main():
    """Runs the program"""
    parser = argparse.ArgumentParser()
    parser.add_argument('word', help='The word to lookup in the dictionary')
    args = parser.parse_args()

    word = args.word.strip().lower()
    output = lookup_word(word)
    print(output)


if __name__ == '__main__':
    main()
