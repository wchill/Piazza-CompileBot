# Piazza-CompileBot
A Piazza bot that executes source code in discussions. Inspired by [CompileBot](https://github.com/renfredxh/compilebot)

### Configuration
Install `requests` and `ideone` using pip or your package manager. (I highly recommend creating a new virtualenv for this.)  
You will also need to install this [Piazza library](https://github.com/wchill/piazza-api); run `python setup.py install`.  
Make a copy of `sample_config.yml` and name it `config.yml`. Edit it with your Piazza username/password and Ideone username/API password.

### Using the bot
The bot will automatically watch any classes it is a member of and check for new/updated posts, submitting the code in the post to Ideone for compilation if any is found.

To call the bot, use the following format:

>CompileBot! python  
>````
>for i in range(1, 101):
>    print i
>````
>Input:
>````
>blah
>````

CompileBot is case-insensitive and any/no punctuation after its name will be ignored. Code and input should be wrapped in code blocks on Piazza. Input is optional and if none is needed the block can be omitted.
