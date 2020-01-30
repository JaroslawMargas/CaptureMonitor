import logging
import HookEvent
# import pyHook
import datetime
import re
import Handler

if __name__ == '__main__':
    # logging.basicConfig(level=logging.INFO)

    # create logger with 'spam_application'
    logger = logging.getLogger('application')
    logger.setLevel(logging.INFO)

    # LogName = str(datetime.datetime.now())
    # logName = re.sub(":", "", LogName) + '.log'
    # # create file handler which logs even debug messages
    # f_handler = logging.FileHandler(logName)
    # f_handler.setLevel(logging.INFO)

    # create console handler with a higher log level
    s_handler = logging.StreamHandler()
    s_handler.setLevel(logging.INFO)

    # create formatter and add it to the handlersArtsiomi_Silivonchyk@epam.com
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # f_handler.setFormatter(formatter)
    s_handler.setFormatter(formatter)

    # add the handlers to the logger
    # logger.addHandler(f_handler)
    logger.addHandler(s_handler)

    logger.info('instance main')

    # hook = HookEvent.HookEvent()
    # hook.hook_mouse_and_key()

    hook = Handler.Handler()
    hook.make_hand()
