from datetime import timedelta
from random import randint, uniform, shuffle
from threading import Thread
from warnings import simplefilter
from time import sleep
from logger import logger

simplefilter('ignore')


class container(dict):
    def writeError(self, message):
        pass


class browserThread:
    from selenium import webdriver
    from fake_useragent import UserAgent

    class Watcher:
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.wait import WebDriverWait
        import selenium.webdriver.support.expected_conditions as EC
        from selenium.webdriver.common.action_chains import ActionChains

        def __init__(self, Browser, Logger):
            self.browser: browserThread.webdriver.Chrome = Browser
            self.logger = Logger
            self.close = False
            self.hanging = False
            self.videoProgress = None
            self.current_time = None
            self.videoPlayer = None
            self.playButton = None
            self.subscribe = None
            self.length = None
            self.body = None
            self.controls = None
            self.settings = None
            self.height = 0
            self.thread = Thread(target=self.watching)
            self.thread.start()

        def watching(self):
            while not self.logger['startAutomation']:
                continue

            try:
                sleep(uniform(0, 10))
                self.logger['Status'] = 'Navigating'
                self.browser.get(self.logger['url'])

                def has_connection(driver):
                    try:
                        driver.find_element_by_xpath('//span[@jsselect="heading" and @jsvalues=".innerHTML:msg"]')
                        return False
                    except:
                        return True

                if not has_connection(self.browser):
                    self.logger['Status'] = 'No internet connection'
                else:
                    if self.logger['id'] not in self.browser.current_url:
                        print('please see the browser it needs to captcha to be solved', self.logger['name'])
                        self.logger['Status'] = 'Solving Captcha'
                    while self.logger['id'] not in self.browser.current_url:
                        continue
                    self.scrapper()

            except:
                self.logger.writeError('watching'.center(100, '-'))
            finally:
                self.logger.clearResources()
                self.browser.quit()

        def scrapper(self):
            try:
                self.logger['Status'] = 'Preparing Variables'
                self.videoPlayer = self.WebDriverWait(self.browser, 10000000).until(
                    self.EC.visibility_of_element_located((self.By.ID, 'movie_player')))
                self.length = self.WebDriverWait(self.browser, 10000000).until(
                    self.EC.visibility_of_element_located((self.By.CLASS_NAME, 'ytp-time-duration')))
                self.current_time = self.WebDriverWait(self.browser, 10000000).until(
                    self.EC.visibility_of_element_located((self.By.CLASS_NAME, "ytp-time-current")))
                self.playButton = self.WebDriverWait(self.browser, 10000000).until(
                    self.EC.visibility_of_element_located((self.By.CLASS_NAME, 'ytp-play-button')))
                self.body = self.WebDriverWait(self.browser, 10000000).until(
                    self.EC.visibility_of_element_located((self.By.ID, 'body')))
                self.controls = self.WebDriverWait(self.browser, 10000000).until(
                    self.EC.presence_of_element_located((self.By.CLASS_NAME, 'ytp-chrome-controls')))
                self.settings = self.WebDriverWait(self.browser, 10000000).until(
                    self.EC.visibility_of_element_located((self.By.CLASS_NAME, 'ytp-settings-button')))
                self.videoProgress = self.WebDriverWait(self.browser, 10000000).until(
                    self.EC.presence_of_element_located((self.By.CLASS_NAME, 'ytp-progress-bar-container')))
                self.height = self.browser.execute_script("return document.body.scrollHeight")

                sleep(uniform(0, 2))
                self.changeQuality(-2)
                sleep(uniform(0, 5))

                self.logger['Status'] = 'Playing Video'
                action = self.ActionChains(self.browser)
                action.move_to_element(self.videoPlayer)
                action.pause(uniform(0, 0.5))
                action.move_to_element(self.playButton)
                action.pause(uniform(0, 0.1))
                action.click()
                action.perform()
                self.logger['Status'] = 'Video Played'

                self.logger['End Time'] = timedelta(
                    seconds=int(self.browser.execute_script('return arguments[0].getDuration();',
                                                            self.videoPlayer)))

                self.logger['Status'] = 'Starting Player Status Thread'
                getPlayerStateThread = self.getPlayerStateThread()
                self.logger['Status'] = 'Starting random Motion Thread'
                randomMotion = self.randomMotion()
                self.logger['Status'] = 'Setting Window Position'
                self.browser.set_window_position(10000, 10000)
                getPlayerStateThread.join()
                randomMotion.join()
            except Exception:
                self.logger.writeError('scrapper'.center(100, '-'))
            finally:
                self.logger.clearResources()
                self.browser.quit()

        def getPlayerStateThread(self):
            def getPlayerState():
                try:
                    duration = int(self.browser.execute_script('return arguments[0].getDuration();', self.videoPlayer))
                    timeState = int(
                        self.browser.execute_script('return arguments[0].getCurrentTime();', self.videoPlayer))
                    playerStatus = int(
                        self.browser.execute_script('return arguments[0].getPlayerState();', self.videoPlayer))
                    self.logger['Estimated Time'] = '%.2f' % (timeState / 3600)
                    self.logger['Current Time'] = timedelta(seconds=timeState)

                    while playerStatus != 0 or timeState >= duration and self.browser.current_url == self.logger['url']:
                        try:
                            if not self.hanging:
                                playerStatus = int(
                                    self.browser.execute_script('return arguments[0].getPlayerState();',
                                                                self.videoPlayer))
                                timeState = int(
                                    self.browser.execute_script('return arguments[0].getCurrentTime();',
                                                                self.videoPlayer))
                                self.logger['Estimated Time'] = '%.2f' % (timeState / 3600)
                                self.logger['Current Time'] = timedelta(seconds=timeState)
                                self.hanging = True
                                while not self.videoPlayer.is_displayed():
                                    self.scrollUp()
                                if playerStatus == 2:
                                    self.logger['Status'] = 'Playing Video'
                                    self.videoPlayer.click()
                                sleep(uniform(0, 0.5))
                        except Exception as e:
                            self.logger.writeError('getPlayerState'.center(100, '-'))
                            pass
                        self.hanging = False
                    self.close = True
                except:
                    self.logger.writeError('getPlayerStateThread'.center(100, '-'))
                finally:
                    self.close = True

            thread = Thread(target=getPlayerState)
            thread.start()
            return thread

        def randomMotion(self):
            def Bot():
                while not self.close:
                    if not self.hanging:
                        try:
                            self.hanging = True
                            self.logger['Status'] = 'Random Motion Started'
                            while not self.videoPlayer.is_displayed():
                                self.scrollUp()
                            self.botToHuman()()
                            sleep(uniform(2, 5))
                        except Exception as e:
                            self.logger.writeError('botToHuman'.center(100, '-'))
                            pass
                        self.hanging = False

            thread = Thread(target=Bot)
            thread.start()
            return thread

        def moveLikeHuman(self, element, maxXRange, maxYRange, spaceLine=50, randomMotion=True):
            def randomPoints(minRange, maxRange, lineSpace):
                minRange = min(minRange, maxRange)
                maxRange = max(minRange, maxRange)
                plots = []
                counter = 0
                while counter <= lineSpace:
                    randomPoint = randint(minRange, maxRange)
                    plots.append(randomPoint)
                    counter += 1
                if not randomMotion:
                    return sorted(plots)
                shuffle(plots)
                return plots

            x_list = randomPoints(0, maxXRange, maxXRange % spaceLine)
            y_list = randomPoints(0, maxYRange, maxYRange % spaceLine)
            y_list += [y_list[-1]] * abs(len(x_list) - len(y_list))
            x_list += [x_list[-1]] * abs(len(x_list) - len(y_list))
            points = list(zip(x_list, y_list))

            self.logger['Status'] = 'Moving From (0, 0) -> (%s, %s) In %s Steps Started' % ( maxXRange, maxYRange, len(points))

            action = self.ActionChains(self.browser)
            action.move_to_element_with_offset(element, 0, 0)

            for (x, y) in points:
                action.move_to_element_with_offset(element, x, y)
            try:
                action.perform()
            except:
                self.logger.writeError('moveLikeHuman'.center(100, '-'))

        def changeQuality(self, number=None, Stop=[0]):
            self.logger['Status'] = 'Changing Video Quality Started'
            Stop[0] += 1
            if Stop[0] < randint(2, 4):
                try:
                    self.settings.click()
                    menuItem = self.browser.find_elements_by_class_name('ytp-menuitem')[-1]
                    sleep(uniform(1, 1.5))
                    menuItem.click()
                    menuItems = self.browser.find_elements_by_class_name('ytp-menuitem')
                    sleep(uniform(1, 1.5))
                    menuItemsLen = len(menuItems)
                    if number is None:
                        number = randint(0, menuItemsLen - 2)
                    if number < menuItemsLen:
                        menuItem = menuItems[number]
                    if not menuItem.is_displayed():
                        self.browser.execute_script('arguments[0].scrollIntoView();', menuItem)
                    sleep(uniform(1, 1.5))
                    menuItem.click()
                    sleep(uniform(1, 1.5))
                except:
                    self.logger['Status'] = 'Changing Video Quality Failed'
                    pass

        def changeViewMode(self):
            try:
                self.logger['Status'] = 'Changing View Mode Started'
                self.videoPlayer.send_keys('t')
            except:
                self.logger['Status'] = 'Changing View Mode Failed'
                pass

        def hoverSeek(self):
            self.logger['Status'] = 'Seek Hovering Started'
            self.moveLikeHuman(self.videoProgress,
                               maxXRange=self.videoProgress.size['width'],
                               maxYRange=self.videoProgress.size['height'],
                               spaceLine=20, randomMotion=False)

        def autoHover(self):
            self.logger['Status'] = 'Hovering Started'
            width = self.browser.execute_script("return window.innerWidth;")
            height = self.browser.execute_script("return window.innerHeight;")
            self.moveLikeHuman(self.body,
                               maxXRange=width,
                               maxYRange=height)

        def hoverInPlayer(self):
            self.logger['Status'] = 'Player Hovering Started'
            self.moveLikeHuman(self.videoPlayer,
                               maxXRange=self.videoPlayer.size['width'],
                               maxYRange=self.videoPlayer.size['height'])

        def mute(self):
            try:
                self.logger['Status'] = 'Muting Video Started'
                action = self.ActionChains(self.browser)
                action.move_to_element(self.videoPlayer)
                action.pause(uniform(0, 0.1))
                action.send_keys('m')
                action.perform()
            except:
                self.logger['Status'] = 'Muting Video Failed'
                pass

        def play(self):
            self.logger['Status'] = 'Playing Video Started'

            def buttonPlay():
                action = self.ActionChains(self.browser)
                action.move_to_element(self.playButton)
                action.pause(uniform(0, 0.1))
                action.click()
                action.perform()

            def clickPlay():
                action = self.ActionChains(self.browser)
                action.move_to_element(self.videoPlayer)
                action.pause(uniform(0, 0.1))
                action.click()
                action.perform()

            def kPlay():
                action = self.ActionChains(self.browser)
                action.move_to_element(self.videoPlayer)
                action.pause(uniform(0, 0.1))
                action.send_keys('k')
                action.perform()

            plays = [buttonPlay, clickPlay, kPlay]

            try:
                plays[randint(0, 2)]
            except:
                self.logger['Status'] = 'Playing Video Failed'
                pass

        def scrollUp(self):
            self.logger['Status'] = 'Scrolling Up'
            self.hanging = True
            for i in range(randint(0, randint(0, self.height % randint(1, 100)))):
                script = '''window.scrollTo(0, -%s)''' % randint(100, 500)
                self.browser.execute_script(script)
                sleep(uniform(0, 0.5))
            self.hanging = False

        def scrollDown(self):
            self.logger['Status'] = 'Scrolling Down'
            self.hanging = True
            for i in range(randint(0, randint(0, self.height % randint(1, 100)))):
                script = '''window.scrollTo(0, %s)''' % randint(100, 500)
                self.browser.execute_script(script)
                sleep(uniform(0, 0.5))
            self.hanging = False

        def botToHuman(self):
            hovers = [self.autoHover, self.changeQuality, self.scrollUp, self.scrollDown,
                      self.changeViewMode, self.mute, self.hoverInPlayer, self.hoverSeek]
            shuffle(hovers)
            return hovers[randint(0, 7)]

    def __init__(self, videoUrl, name='TPCTWatcher', chromeExecutablePath='./chromedriver', proxy=None,
                 logging=True):
        self.browser = None
        self.logger = container()
        fakeUseragent = self.UserAgent()
        chromeOptions = self.webdriver.ChromeOptions()

        chromeOptions.add_argument('--mute-audio')
        chromeOptions.add_argument('user-agent=%s' % fakeUseragent)
        chromeOptions.add_argument('window-size=%s,%s' % (randint(520, 720), randint(480, 720)))
        chromeOptions.add_argument("disable-infobars")
        chromeOptions.add_argument("--disable-popup-blocking")
        chromeOptions.add_argument("--disable-notifications")
        chromeOptions.add_experimental_option("excludeSwitches", ["enable-automation", 'enable-logging'])
        chromeOptions.add_experimental_option('useAutomationExtension', False)

        for i in range(4):
            chromeOptions.add_extension('./vpn%s.crx' % i)

        if proxy is not None:
            chromeOptions.add_argument('--proxy-server=%s' % proxy)

        if logging:
            self.logger = logger(logMessageTemplate='%s',
                                 logMessageArguments=('Name', 'Current Time', 'End Time', 'Estimated Time', 'Status'),
                                 updateOn=('Current Time', 'Status'),
                                 validFilePath='', invalidFilePath='',
                                 finishedFilePath='', responseFilePath='')

        self.logger['Estimated Time'] = 0
        self.browser = self.webdriver.Chrome(executable_path=chromeExecutablePath, chrome_options=chromeOptions)
        self.browser.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                            Object.defineProperty(navigator, 'webdriver', {
                              get: () => undefined
                            })
                          """
        })

        self.browser.execute_cdp_cmd("Network.enable", {})
        self.logger['Name'] = name
        self.logger['name'] = name
        self.logger['url'] = videoUrl
        self.logger['id'] = videoUrl.split('=')[-1]
        self.logger['startAutomation'] = False
        self.thread = self.Watcher(self.browser, self.logger).thread

    def close(self):
        try:
            self.browser.quit()
        except:
            pass


if __name__ == '__main__':
    url = 'https://www.youtube.com/watch?v='
    browsers = []

    for i in range(10):
        WatchingBrowser = browserThread(url, name='TPCTWatcher%s' % i)
        browsers.append(WatchingBrowser)
        input('please press enter to start full automation: ')
        WatchingBrowser.logger['startAutomation'] = True

    for browser in browsers:
        browser.thread.join()
