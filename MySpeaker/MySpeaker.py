###############################################################################
import win32com.client
###############################################################################
# https://zenn.dev/decl/articles/4efdf0b7fef861
# https://w.atwiki.jp/ceviouser/pages/70.html#id_69e464ba
###############################################################################
class MySpeaker:
    ###############################################################################
    def __init__(self):
        cevio = win32com.client.Dispatch("CeVIO.Talk.RemoteService2.ServiceControl2")
        cevio.StartHost(False)
        self.talker = win32com.client.Dispatch("CeVIO.Talk.RemoteService2.Talker2V40")
        self.talker.Cast = "さとうささら"
        self.status = "ON"    
    ###############################################################################
    def setCast(self, cast):
        self.talker.Cast = cast
    ###############################################################################
    def setToneScale(self, tone_scale):
        self.talker.ToneScale = tone_scale
    ###############################################################################
    def setSpeed(self, speed):
        self.talker.Speed = speed
    ###############################################################################
    def speak(self, text):
        if self.status == "ON":
            state = self.talker.Speak(text)
            state.Wait()
    ###############################################################################
    def off(self):
        self.status = "OFF"
    ###############################################################################
    def on(self):
        self.status = "ON"
###############################################################################
if __name__ == '__main__':
    speaker = MySpeaker()
    speaker.setCast("さとうささら")
    speaker.setToneScale(100)
    speaker.setSpeed(30)
    speaker.speak("しゃべらせたいテキスト")
###############################################################################