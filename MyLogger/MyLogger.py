################################################################################
import traceback
import time
import re
import os
import logging
import inspect
import coloredlogs
from datetime import datetime
import sys
sys.path.append("../MySpeaker/")
################################################################################
if 1:  # format回避のためにネストを下げる
    from MySpeaker import MySpeaker
################################################################################


class MyLogger:
    LEVEL_TABLE = {
        'spam': {'level': 'SPAM', 'value': 5},          'SPAM': {'level': 'SPAM', 'value': 5},
        'debug': {'level': 'DEBUG', 'value': 10},       'DEBUG': {'level': 'DEBUG', 'value': 10},
        'verbose': {'level': 'VERBOSE', 'value': 15},   'VERBOSE': {'level': 'VERBOSE', 'value': 15},
        'info': {'level': 'INFO', 'value': 20},         'INFO': {'level': 'INFO', 'value': 20},
        'notice': {'level': 'NOTICE', 'value': 25},     'NOTICE': {'level': 'NOTICE', 'value': 25},
        'warning': {'level': 'WARNING', 'value': 30},   'WARNING': {'level': 'WARNING', 'value': 30},
        'success': {'level': 'SUCCESS', 'value': 35},   'SUCCESS': {'level': 'SUCCESS', 'value': 35},
        'error': {'level': 'ERROR', 'value': 40},       'ERROR': {'level': 'ERROR', 'value': 40},
        'critical': {'level': 'CRITICAL', 'value': 50}, 'CRITICAL': {'level': 'CRITICAL', 'value': 50},
        'sakura': {'level': 'SAKURA', 'value': 99},     'SAKURA': {'level': 'SAKURA', 'value': 99}
    }
    ################################################################################

    def __init__(self, name='NO_NAME', level='DEBUG', speaker=None):
        # メンバ変数初期化
        self.level = self.LEVEL_TABLE[level]['level']
        self.stacks = {}
        self.stack_level = 0
        self.speaker = speaker
        self.external_speaker_status = "ON"
        # ログレベル追加
        logger = logging.getLogger(name)
        logging.SPAM = self.LEVEL_TABLE['SPAM']['value']
        logging.VERBOSE = self.LEVEL_TABLE['VERBOSE']['value']
        logging.NOTICE = self.LEVEL_TABLE['NOTICE']['value']
        logging.SUCCESS = self.LEVEL_TABLE['SUCCESS']['value']
        logging.SAKURA = self.LEVEL_TABLE['SAKURA']['value']
        logging.addLevelName(logging.SPAM, 'SPAM')
        logging.addLevelName(logging.VERBOSE, 'VERBOSE')
        logging.addLevelName(logging.NOTICE, 'NOTICE')
        logging.addLevelName(logging.SUCCESS, 'SUCCESS')
        logging.addLevelName(logging.SAKURA, 'SAKURA')
        setattr(logger, 'spam', lambda message, *
                args: logger._log(logging.SPAM, message, args))
        setattr(logger, 'verbose', lambda message, *
                args: logger._log(logging.VERBOSE, message, args))
        setattr(logger, 'notice', lambda message, *
                args: logger._log(logging.NOTICE, message, args))
        setattr(logger, 'success', lambda message, *
                args: logger._log(logging.SUCCESS, message, args))
        setattr(logger, 'sakura', lambda message, *
                args: logger._log(logging.SAKURA, message, args))
        # 自作ログ関数を噛ませるために、オリジナルを保存
        self.origin_log_func_map = {}
        self.origin_log_func_map["SAKURA"] = logger.sakura
        self.origin_log_func_map["CRITICAL"] = logger.critical
        self.origin_log_func_map["ERROR"] = logger.error
        self.origin_log_func_map["SUCCESS"] = logger.success
        self.origin_log_func_map["WARNING"] = logger.warning
        self.origin_log_func_map["NOTICE"] = logger.notice
        self.origin_log_func_map["INFO"] = logger.info
        self.origin_log_func_map["VERBOSE"] = logger.verbose
        self.origin_log_func_map["DEBUG"] = logger.debug
        self.origin_log_func_map["SPAM"] = logger.spam
        self.origin_log = logger._log
        logger._log = self._log
        # コンソール上のログを色付け
        coloredlogs.CAN_USE_BOLD_FONT = True
        coloredlogs.DEFAULT_FIELD_STYLES = {
            'asctime': {'color': 'green'},
            'hostname': {'color': 'magenta'},
            'levelname': {'color': 'black', 'bold': True},
            'name': {'color': 'blue'},
            'programname': {'color': 'cyan'}
        }
        coloredlogs.DEFAULT_LEVEL_STYLES = {
            'info': {},
            'notice': {'color': 'magenta'},
            'verbose': {'color': 'blue'},
            'success': {'color': 'green', 'bold': True},
            'spam': {'color': 'cyan'},
            'critical': {'color': 'red', 'bold': True},
            'error': {'color': 'red'},
            'debug': {'color': 'green'},
            'warning': {'color': 'yellow'},
            'sakura': {'color': 200, 'bold': True},
        }
        coloredlogs.install(level=level, logger=logger,
                            fmt='[ %(asctime)s ][ %(levelname)8s ][ ' + name + ' ][ %(funcName)6s ][ %(message)s ]', datefmt='%H:%M:%S')
        # ログをファイル出力
        basedir = os.path.dirname(os.path.abspath(__file__))+'/log/'
        if not os.path.exists(basedir):
            os.makedirs(basedir)
        filename = datetime.now().strftime('%Y%m%d_%H%M') + '_' + name + '.log'
        handler = logging.FileHandler(basedir + filename, 'w', 'utf-8')
        handler.setFormatter(logging.Formatter(
            '[ %(asctime)s ][ %(levelname)8s ][ ' + name + ' ][ %(funcName)6s ][ %(message)s ]', datefmt='%H:%M:%S'))
        logger.addHandler(handler)

################################################################################
    # @brief インスタンス取得
    @classmethod
    def GetInstance(cls, name='NO_NAME', level='DEBUG', speaker=None):
        # ファイルごとに出力レベルを管理するので、一番低いレベルを設定しておく。
        if not hasattr(cls, 'instance_map'):
            cls.instance_map = {}
        if not name in cls.instance_map:
            cls.instance_map[name] = cls(name, level, speaker)
        return cls.instance_map[name]
################################################################################
    # オリジナルログ関数を使用したときに、
    # 呼び出し元関数が良い感じにログに表示されるように
    # stacklevelを調整している。

    def _log(self, level, msg, args, exc_info=None, extra=None, stack_info=False, stack_level=4):
        self.origin_log(level, msg, args, exc_info,
                        extra, stack_info, stack_level)
################################################################################

    def printLog(self, level, *args, **kwargs):
        level = self.LEVEL_TABLE[level]['level']
        frameinfo = inspect.stack()[2]
        filename = os.path.basename(frameinfo.filename)
        if self.isNeedToLog(level):
            self.origin_log_func_map[level](
                self.makeMessage(args, filename, frameinfo.lineno))
        if self.speaker:
            self.speaker.speak(args)
################################################################################

    def makeMessage(self, args, filename, lineno):
        msg = ''
        for arg in args:
            msg += str(arg) + " "
        msg = '[' + filename + ':' + str(lineno) + '] ' + msg
        if msg.find('\n') != -1:
            msg = msg.strip(" ")
            msg = msg.strip("\t")
            msg = '\n' + msg + '\n'
        return msg
################################################################################

    def isNeedToLog(self, level):
        return self.LEVEL_TABLE[level]['value'] >= self.LEVEL_TABLE[self.level]['value']
################################################################################

    def sakura(self, *args, **kwargs):
        self.printLog("SAKURA", *args, **kwargs)
################################################################################

    def critical(self, *args, **kwargs):
        self.printLog("CRITICAL", *args, **kwargs)
################################################################################

    def error(self, *args, **kwargs):
        self.printLog("ERROR", *args, **kwargs)
################################################################################

    def success(self, *args, **kwargs):
        self.printLog("SUCCESS", *args, **kwargs)
################################################################################

    def warning(self, *args, **kwargs):
        self.printLog("WARNING", *args, **kwargs)
################################################################################

    def notice(self, *args, **kwargs):
        self.printLog("NOTICE", *args, **kwargs)
################################################################################

    def info(self, *args, **kwargs):
        self.printLog("INFO", *args, **kwargs)
################################################################################

    def verbose(self, *args, **kwargs):
        self.printLog("VERBOSE", *args, **kwargs)
################################################################################

    def debug(self, *args, **kwargs):
        self.printLog("DEBUG", *args, **kwargs)
################################################################################

    def spam(self, *args, **kwargs):
        self.printLog("SPAM", *args, **kwargs)
################################################################################

    def showTrace(self, func):
        def decowrapper(*args, **kwargs):
            try:
                pwd = os.getcwd()
                self.start()
                ret = func(*args, **kwargs)
                self.finish()
                os.chdir(pwd)
                return ret
            except Exception as e:
                self.__speakOff()
                self.critical("+++++++++++++++++++++++++++++++++++")
                for i in range(len(self.stacks)):
                    stack = self.stacks[i].copy()
                    del stack['start']
                    self.critical(stack)
                self.critical("+++++++++++++++++++++++++++++++++++")
                self.critical(type(e))
                self.critical(e)
                self.critical(traceback.format_exc())
                self.critical("+++++++++++++++++++++++++++++++++++")
                self.__speakOn()
                input("press any key to exit ...")
                sys.exit()
        return decowrapper
################################################################################

    def start(self):
        frameinfo = inspect.stack()[2]
        filename = os.path.basename(frameinfo.filename)
        lineno = str(frameinfo.lineno)
        code_context = frameinfo.code_context[0]

        self.stacks[self.stack_level] = {}
        current_stack = self.stacks[self.stack_level]
        current_stack['level'] = ('■' * (self.stack_level) + '□□□□□□□□□□')[:10]
        current_stack['file'] = filename + ":" + lineno
        current_stack['func'] = re.sub("\s*(.*)\n", "\\1", code_context)
        current_stack['start'] = round(time.time(), 2)

        for i in range(len(self.stacks)):
            start = self.stacks[i]['start']
            elapsedTime = round(time.time() - start, 2)
            self.stacks[i]['elapsedTime'] = elapsedTime

        self.stack_level += 1
        self.__speakOff()
        self.debug("+++++++++++++++++++++++++++++++++++")
        for i in range(len(self.stacks)):
            stack = self.stacks[i].copy()
            del stack['start']
            if i == len(self.stacks)-1:
                self.debug("Enter >>>", stack)
            else:
                self.debug("         ", stack)
        self.debug("+++++++++++++++++++++++++++++++++++")
        self.__speakOn()
################################################################################

    def finish(self):
        for i in range(len(self.stacks)):
            start = self.stacks[i]['start']
            elapsedTime = round(time.time() - start, 2)
            self.stacks[i]['elapsedTime'] = elapsedTime
        self.__speakOff()
        self.debug("+++++++++++++++++++++++++++++++++++")
        for i in range(len(self.stacks)):
            stack = self.stacks[i].copy()
            del stack['start']
            if i == len(self.stacks)-1:
                self.debug("Exit  <<<", stack)
            elif i == len(self.stacks)-2:
                self.debug("Enter >>>", stack)
            else:
                self.debug("         ", stack)
        self.debug("+++++++++++++++++++++++++++++++++++")
        self.__speakOn()
        self.stack_level -= 1
        del self.stacks[self.stack_level]
################################################################################

    def speakOn(self):
        self.external_speaker_status = "ON"
        self.__speakOn()
################################################################################

    def speakOff(self):
        self.external_speaker_status = "OFF"
        self.__speakOff()
################################################################################

    def __speakOn(self):
        # 外部からoffに設定されているときはonにしない
        if self.external_speaker_status == "OFF":
            return
        if self.speaker:
            self.speaker.on()
################################################################################

    def __speakOff(self):
        if self.speaker:
            self.speaker.off()
################################################################################

    def getElapsedTime(self):
        if len(self.stacks) < 1:
            return False
        # 全てのframeの経過時間を計算
        for i in range(len(self.stacks)):
            start = self.stacks[i]['start']
            elapsedTime = round(time.time() - start, 2)
            self.stacks[i]['elapsedTime'] = elapsedTime
        return self.stacks[self.stack_level-1]['elapsedTime']
################################################################################

    def isTimeout(self, second):
        if len(self.stacks) < 1:
            return False
        # 全てのframeの経過時間を計算
        for i in range(len(self.stacks)):
            start = self.stacks[i]['start']
            elapsedTime = round(time.time() - start, 2)
            self.stacks[i]['elapsedTime'] = elapsedTime
        # timeout判定
        elapsedTime = self.stacks[self.stack_level-1]['elapsedTime']
        if second < elapsedTime:
            self.__speakOff()
            self.warning(elapsedTime, "/", second, "elapsed")
            self.__speakOn()
            return True
        else:
            self.__speakOff()
            self.debug(elapsedTime, "/", second, "elapsed")
            self.__speakOn()
            return False
###############################################################################

    def sleep(self, second):
        if second <= 0:
            self.ERROR("argument second is negative or zero")
            return
        start = round(time.time(), 2)
        while 1:
            elapsed = round(time.time() - start, 2)
            if elapsed >= second:
                break
            time.sleep(1)
            self.__speakOff()
            self.debug("time sleeping " + str(elapsed) + " / " + str(second))
            self.__speakOn()


###############################################################################
if __name__ == '__main__':
    speaker = MySpeaker()
    logger = MyLogger('TEST1', 'spam', speaker)

    @logger.showTrace
    def test1():
        logger.sakura('This is SAKURA. (99)')
        logger.critical('This is CRITICAL. (50)')
        logger.error('This is ERROR. (40)')
        logger.success('This is SUCCESS. (35)')
        logger.warning('This is WARNING. (30)')
        logger.notice('This is NOTICE. (25)')
        logger.info('This is INFO. (20)')
        logger.verbose('This is VERBOSE. (15)')
        logger.debug('This is DEBUG. (10)')
        logger.spam('This is SPAM. (5)')

    @logger.showTrace
    def test2():
        while not logger.isTimeout(10):
            logger.sleep(3)
    test1()
    test2()
###############################################################################
