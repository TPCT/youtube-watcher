import traceback


class logger:
    from os import path

    class log:
        from sys import stdout
        from threading import Thread

        def __init__(self, logFile=None, logMessageTemplate=None, logMessageArgs=None, updateOn=None):
            self.logFile = open(logFile, 'a+') if logFile else None
            self.parsedMessage = ''
            self.logMessageTemplate = logMessageTemplate if logMessageTemplate else ''
            self.logMessageArgs = logMessageArgs
            self.updateOn = updateOn if updateOn else tuple()
            self.stop = False
            self.items = [item for item in self.__dict__
                          if not item.startswith('__')
                          and item not in ('stdout', 'logFile', 'website',
                                           'logFileWriter', 'stdoutWriter', 'message',
                                           'messageData', 'clearResources', 'stdoutThread',
                                           'Thread', 'stop', 'logMessageTemplate', 'logMessageArgs', 'updateOn')]
            for item in logMessageArgs:
                self[item] = ''
            self.stdoutThread = self.Thread(target=self.stdoutWriter)
            self.stdoutThread.start()

        def __getitem__(self, key):
            if key in self.items:
                return self.__getattribute__(key)

        def __setitem__(self, key, value):
            if key in self.items and value != self.__getattribute__(key):
                self.__setattr__(key, value)
                if key in self.updateOn:
                    if self.logMessageTemplate and self.logMessageArgs:
                        messageData = ['%s: %s' % (x, self[x]) for x in self.logMessageArgs]
                        self.parsedMessage = self.logMessageTemplate % ' - '.join(messageData)
                        self.logFileWriter(self.parsedMessage)
            else:
                self.__setattr__(key, value)
                self.items.append(key)

        def stdoutWriter(self, msg=['']):
            while not self.stop:
                try:
                    if not self.stdout.closed:
                        if msg[0] != self.parsedMessage:
                            self.stdout.write('%s\n' % self.parsedMessage)
                            self.stdout.flush()
                            msg[0] = self.parsedMessage
                except KeyboardInterrupt:
                    continue

        def logFileWriter(self, message):
            while True:
                try:
                    if self.logFile:
                        if self.logFile.closed:
                            self.logFile = open(self.logFile.name, 'a+')
                        self.logFile.write('%s\n' % message)
                        self.logFile.flush()
                        break
                except KeyboardInterrupt:
                    continue

        def clearResources(self):
            while not self.logFile.closed:
                try:
                    self.logFile.close() if not self.logFile.closed else None
                    self.stop = True
                    self.stdoutThread.join()
                except KeyboardInterrupt:
                    continue
                except Exception:
                    pass

    def __init__(self, errFilePath='err.txt', outputFilePath='log.txt',
                 validFilePath='valid.txt', invalidFilePath='invalid.txt',
                 finishedFilePath='finished.txt', responseFilePath='resp.txt',
                 logMessageTemplate='', logMessageArguments=tuple(), updateOn=()):
        errFilePath = errFilePath if errFilePath else 'err.txt'
        self.errFile = open(errFilePath, 'w+')
        self.invalidFile = open(invalidFilePath, 'w+') if invalidFilePath else None
        self.finishedFile = open(finishedFilePath, 'r+' if self.path.isfile(finishedFilePath) else 'w+') if finishedFilePath else None
        self.responseFile = open(responseFilePath, 'w+') if responseFilePath else None
        self.validFile = open(validFilePath, 'a+') if validFilePath else None
        self.logging = self.log(outputFilePath,
                                logMessageTemplate=logMessageTemplate,
                                logMessageArgs=logMessageArguments,
                                updateOn=updateOn)

    def __setitem__(self, key, value):
        self.logging[key] = value

    def __getitem__(self, item):
        return self.logging[item]

    def writeError(self, message):
        while True:
            try:
                if self.errFile:
                    if self.errFile.closed:
                        self.errFile = open(self.errFile.name, 'a+')
                    self.errFile.write('%s\n' % message)
                    self.errFile.write(traceback.format_exc())
                    self.errFile.flush()
                    break
            except KeyboardInterrupt:
                continue

    def respWriter(self, message):
        while True:
            try:
                if self.responseFile:
                    if self.responseFile.closed:
                        self.responseFile = open(self.responseFile.name, 'a+')
                    self.responseFile.write('%s\n' % message)
                    self.responseFile.flush()
                    break
            except KeyboardInterrupt:
                continue

    def validWriter(self, line):
        while True:
            try:
                if self.invalidFile:
                    if self.invalidFile.closed:
                        self.validFile = open(self.invalidFile.name, 'a+')
                    self.validFile.write('%s\n' % line)
                    self.finishedFile.write('%s\n' % line)
                    self.validFile.flush()
                    self.finishedFile.flush()
                    break
            except KeyboardInterrupt:
                continue

    def invalidWriter(self, line):
        while True:
            try:
                if self.invalidFile:
                    if self.invalidFile.closed:
                        self.invalidFile = open(self.invalidFile.name, 'a+')
                    self.invalidFile.write('%s\n' % line)
                    self.finishedFile.write('%s\n' % line)
                    self.invalidFile.flush()
                    self.finishedFile.flush()
                    break
            except KeyboardInterrupt:
                continue

    def finishedWriter(self, line):
        while True:
            try:
                if self.finishedFile:
                    if self.finishedFile.closed:
                        self.finishedFile = open(self.finishedFile.name, 'a+')
                    self.finishedFile.write('%s\n' % line)
                    self.finishedFile.flush()
                    break
            except KeyboardInterrupt:
                pass

    def clearResources(self):
        while not all([self.validFile.closed if self.validFile else True,
                       self.invalidFile.closed if self.invalidFile else True,
                       self.finishedFile.closed if self.finishedFile else True,
                       self.responseFile.closed if self.responseFile else True]):
            try:
                self.validFile.close() if self.validFile and not self.validFile.closed else None
                self.invalidFile.close() if self.invalidFile and not self.invalidFile.closed else None
                self.finishedFile.close() if self.finishedFile and not self.finishedFile.closed else None
                self.responseFile.close() if self.responseFile and not self.responseFile.closed else None
            except KeyboardInterrupt:
                continue
            except Exception:
                self.writeError('clearResources(logger)'.center(100, '-'))
        self.logging.clearResources()


if __name__ == '__main__':
    loggingClass = logger(logMessageTemplate='%s',
                          logMessageArguments=('name', 'age'), updateOn=('age',),
                          validFilePath='', invalidFilePath='',
                          finishedFilePath='', responseFilePath='')
    loggingClass['name'] = 'islam'
    loggingClass['age'] = 21
    loggingClass['name'] = 'mohamed'
    loggingClass['age'] = 22
    loggingClass.clearResources()

