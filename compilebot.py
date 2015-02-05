# Some code taken from CompileBot: https://github.com/renfredxh/compilebot

from piazza_api import Piazza
from piazza_api.network import UnreadFilter
import ideone
import time
from datetime import datetime
from bs4 import BeautifulSoup
import re
import urllib

from config import *

class PiazzaCompileBot(object):
    
    def __init__(self):
        self.p = Piazza()
        self.p.user_login(PIAZZA_USER, PIAZZA_PASS)

        classes = self.p.get_user_classes()
        self.classes = []

        print 'Now watching posts for the following {0} classes:'.format(len(classes))
        for c in classes:
            print '{0} ({1}, {2})'.format(c['num'], c['name'], c['term'])
            self.classes.append(self.p.network(c['nid']))

            self.filter = UnreadFilter()

    def check(self):
        for c in self.classes:

            # ensure we go through the entire feed if there are more posts to read
            feed = {'more': True}
            while feed['more']:
                # filter for only updated posts
                feed = c.get_filtered_feed(self.filter)
                for feed_post in feed['feed']:
                    # get the post number and retrieve the post
                    post = c.get_post(feed_post['nr'])
                    post_text = post['history'][0]['content']

                    # parse the text in the post
                    # example text:
                    """
                    <p></p><p>I&#39;m having an issue, please help!</p>
                    <p>CompileBot! python</p>
                    <pre>def __init__(self):
                        print &#39;blah&#39;</pre>
                    <p>Input:</p>
                    <pre>blah</pre>
                    """
                    soup = BeautifulSoup(post_text)
                    # Look for p tags
                    tags = soup.find_all('p')
                    for tag in tags:
                        try:
                            m = None if not tag.contents else re.search(r'(?i)CompileBot[.?;:!]*\s*(?P<args>.*)\s*', tag.contents[0])
                            if m is not None:
                                # look for code
                                code = None
                                cur_tag = tag.next_sibling
                                if cur_tag.name == 'pre':
                                    code = cur_tag.contents[0]
                                    cur_tag = cur_tag.next_sibling
                                elif cur_tag.next_sibling.name == 'pre':
                                    code = cur_tag.next_sibling.contents[0]
                                    cur_tag = cur_tag.next_sibling.next_sibling

                                # look for optional stdin
                                if code is not None:
                                    stdin = ''
                                    try:
                                        if cur_tag.name == 'p' and bool(re.match('input'), cur_tag.contents[0], re.I):
                                            cur_tag = tag.next_sibling
                                            if cur_tag.name == 'pre':
                                                stdin = cur_tag.contents[0]
                                                cur_tag = cur_tag.next_sibling
                                            elif cur_tag.next_sibling.name == 'pre':
                                                stdin = cur_tag.next_sibling.contents[0]
                                                cur_tag = cur_tag.next_sibling.next_sibling
                                    except:
                                        pass
                                    code = urllib.unquote(code)
                                    stdin = urllib.unquote(stdin)
                                    try:
                                        lang, opts = m.group('args').split(' -', 1)
                                        opts = ('-' + opts).split()
                                    except ValueError:
                                        # No additional opts found
                                        lang, opts = m.group('args'), []
                                    lang = lang.strip()
                                    print 'Attempting compile for comment {0}: language={1}, args={2}'.format(post['id'], lang, opts)
                                    try:
                                        details = self.compile(code, lang, stdin=stdin)
                                        print "Compiled ideone submission {link} for comment {id}".format(link=details['link'], id=post['id'])
                                    except ideone.IdeoneError as e:
                                        print e
                                    # The ideone submission result value indicaties the final state of
                                    # the program. If the program compiled and ran successfully the
                                    # result is 15. Other codes indicate various errors.
                                    result_code = details['result']
                                    # The user is alerted of any errors via message reply unless they
                                    # include an option to include errors in the reply.
                                    if result_code == 15 or ('--include-errors' in opts and result_code in [11, 12]):
                                        text = self.format_reply(details, opts)
                                        ideone_link = "http://ideone.com/{}".format(details['link'])
                                        text += "Ideone link: %s" % ideone_link
                                        print 'Compilation success!\n%s' % text
                                    else:
                                        error_text = {
                                            11: COMPILE_ERROR_TEXT,
                                            12: RUNTIME_ERROR_TEXT,
                                            13: TIMEOUT_ERROR_TEXT,
                                            17: MEMORY_ERROR_TEXT,
                                            19: ILLEGAL_ERROR_TEXT,
                                            20: INTERNAL_ERROR_TEXT
                                        }.get(result_code, '')
                                        # Include any output from the submission in the reply.
                                        if details['cmpinfo']:
                                            error_text += "Compiler Output:\n\n{}\n\n".format(
                                                                code_block(details['cmpinfo']))
                                        if details['output']:
                                            error_text += "Output:\n\n{}\n\n".format(
                                                    code_block(details['output']))
                                        if details['stderr']:
                                            error_text += "Error Output:\n\n{}\n\n".format(
                                                                code_block(details['stderr']))
                                        print 'Error: %s' % error_text
                        except ValueError as e:
                            import traceback, os.path, sys
                            top = traceback.extract_tb(sys.exc_info()[2])[-1]
                            print 'Parse failed: {0}'.format(', '.join([type(e).__name__, os.path.basename(top[0]), str(top[1])]))


    def compile(self, source, lang, stdin=''):
        """Compile and evaluate source sode using the ideone API and return
        a dict containing the output details.
        Keyword arguments:
        source -- a string containing source code to be compiled and evaluated
        lang -- the programming language pertaining to the source code
        stdin -- optional "standard input" for the program
        >>> d = compile('print("Hello World")', 'python')
        >>> d['output']
        Hello World
        """
        lang = LANG_ALIASES.get(lang.lower(), lang)
        # Login to ideone and create a submission
        i = ideone.Ideone(IDEONE_USER, IDEONE_PASS)
        sub = i.create_submission(source, language_name=lang, std_input=stdin)
        sub_link = sub['link']
        details = i.submission_details(sub_link)
        # The status of the submission indicates whether or not the source has
        # finished executing. A status of 0 indicates the submission is finished.
        while details['status'] != 0:
            details = i.submission_details(sub_link)
            time.sleep(3)
        details['link'] = sub_link
        return details

    def format_reply(self, details, opts):
        """Returns a reply that contains the output from a ideone submission's
        details along with optional additional information.
        """
        head, body, extra, = '', '', ''
        # Combine information that will go before the output.
        if '--source' in opts:
            head += 'Source:\n{}\n\n'.format(code_block(details['source']))
        if '--input' in opts:
        # Combine program output and runtime error output.
            head += 'Input:\n{}\n\n'.format(code_block(details['input']))
        output = details['output'] + details['stderr']
        # Truncate the output if it contains an excessive
        # amount of line breaks or if it is too long.
        if output.count('\n') > LINE_LIMIT:
            lines = output.split('\n')
            # If message contains an excessive amount of duplicate lines,
            # truncate to a small amount of lines to discourage spamming
            if len(set(lines)) < 5:
                lines_allowed = 2
            else:
                lines_allowed = 51
            output = '\n'.join(lines[:lines_allowed])
            output += "\n..."
        # Truncate the output if it is too long.
        if len(output) > 8000:
            output = output[:8000] + '\n    ...\n'
        body += 'Output:\n{}\n\n'.format(output)
        if details['cmpinfo']:
            body += 'Compiler Info:\n{}\n\n'.format(details['cmpinfo'])
        # Combine extra runtime information.
        if '--date' in opts:
            extra += "Date: {}\n\n".format(details['date'])
        if '--memory' in opts:
            extra += "Memory Usage: {} bytes\n\n".format(details['memory'])
        if '--time' in opts:
            extra += "Execution Time: {} seconds\n\n".format(details['time'])
        if '--version' in opts:
            extra += "Version: {}\n\n".format(details['langVersion'])
        # To ensure the reply is less than 10000 characters long, shorten
        # sections of the reply until they are of adequate length. Certain
        # sections with less priority will be shortened before others.
        total_len = 0
        for section in (FOOTER, body, head, extra):
            if len(section) + total_len > 9800:
                section = section[:9800 - total_len] + '\n...\n'
                total_len += len(section)
        reply_text = head + body + extra
        return reply_text


# example usage

if __name__ == '__main__':
    bot = PiazzaCompileBot()
    while True:
        bot.check()
        sleeptime = 60 - datetime.utcnow().second
        time.sleep(sleeptime)