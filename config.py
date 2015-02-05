# based off of CompileBot's config.py

import os
import yaml

# Configuration
CONFIG_FILE = 'config.yml'

# Fetch settings from YAML file
try:
    with open(CONFIG_FILE, 'r') as f:
        CONFIG = yaml.load(f)
except (OSError, IOError) as e:
    print("Please configure config.yml")
    exit(1)

# File for logging. Default is STDOUT.
LOG_FILE = CONFIG['log_file']

# Login credentials
IDEONE_USER = os.environ.get('IDEONE_USER') or CONFIG['ideone_user']
IDEONE_PASS = os.environ.get('IDEONE_PASS') or CONFIG['ideone_pass']
PIAZZA_USER = os.environ.get('PIAZZA_USER') or CONFIG['piazza_user']
PIAZZA_PASS = os.environ.get('PIAZZA_PASS') or CONFIG['piazza_pass']

LANG_ALIASES = {k.lower(): v for k, v in CONFIG['lang_aliases'].items()}

# A set of users that are banned. The banned users list is retrieved
# in the main session but not here because it requires a reddit login.
BANNED_USERS = set()

# Spam Settings
LINE_LIMIT = os.environ.get('COMPILEBOT_SPAM_LINE_LIMIT') or CONFIG['spam']['line_limit']
CHAR_LIMIT = os.environ.get('COMPILEBOT_SPAM_CHAR_LIMIT') or CONFIG['spam']['char_limit']
SPAM_PHRASES = os.environ.get('COMPILEBOT_SPAM_SPAM_PHRASES') or CONFIG['spam']['spam_phrases']
IGNORE_SPAM = os.environ.get('COMPILEBOT_SPAM_IGNORE') or CONFIG['spam']['ignore']
# Perform necessary conversions for environment variable strings
if isinstance(LINE_LIMIT, str): LINE_LIMIT = int(LINE_LIMIT)
if isinstance(CHAR_LIMIT, str): CHAR_LIMIT = int(CHAR_LIMIT)
if isinstance(SPAM_PHRASES, str): SPAM_PHRASES = SPAM_PHRASES.split(',')
if isinstance(IGNORE_SPAM, str): IGNORE_SPAM = IGNORE_SPAM.split(',')

# Text
TEXT = CONFIG['text']
FOOTER = TEXT['footer']
ERROR_PREAMBLE = TEXT['error_preamble']
ERROR_POSTAMBLE = TEXT['error_postamble']
HELP_TEXT = TEXT['help_text']
LANG_ERROR_TEXT = TEXT['language_error_text']
FORMAT_ERROR_TEXT = TEXT['format_error_text']
COMPILE_ERROR_TEXT = TEXT['compile_error_text']
RUNTIME_ERROR_TEXT = TEXT['runtime_error_text']
TIMEOUT_ERROR_TEXT = TEXT['timeout_error_text']
MEMORY_ERROR_TEXT = TEXT['memory_error_text']
ILLEGAL_ERROR_TEXT = TEXT['illegal_error_text']
INTERNAL_ERROR_TEXT =  TEXT['internal_error_text']
RECOMPILE_ERROR_TEXT = TEXT['recompile_error_text']
RECOMPILE_AUTHOR_ERROR_TEXT = TEXT['recompile_author_error_text']
