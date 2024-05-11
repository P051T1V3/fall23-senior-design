from datetime import datetime
import time
import os

from kivymd.app import MDApp
from kivymd.uix.button import MDRaisedButton
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.core.audio import SoundLoader
from kivy.properties import ObjectProperty

from kivy.clock import Clock
from kivy.lang import Builder

from plyer import filechooser
from pydub import AudioSegment

from HealthTools import *

class AudioInterface(TabbedPanel):
    audio = ObjectProperty()
    sound = None
    left_of = 0
    template_path = None
    audio_path = None
    summary = None
    transcript = None
    clk = None
    sentences = list()
    
    def audio_chooser(self):
        filechooser.open_file(on_selection=self.select_audio)

    def select_audio(self, selection):
        # Selection = audio_path 
        if selection:
            self.audio_path = selection[0]
            self.ids["audio_loc"].text = "Ses dosyasının adresi: " + str(self.audio_path)
            self.sound = SoundLoader.load(self.audio_path)
            self.update_buttons()

    def template_chooser(self):
        filechooser.open_file(on_selection=self.select_template)

    def select_template(self, selection):
        # Selection burada seçtiğin dosyanın file_path oluyo
        if selection:
            self.template_path = selection[0]
            self.ids["template_loc"].text = "Rapor taslağının adresi: " + str(self.template_path)
            self.update_buttons()
            

    def play_sound(self):
        if self.sound:
            state = self.sound.state
            if state == "play":
                self.clk.cancel
                self.left_of = self.sound.get_pos() # get_pos() saniye veriyo
                self.sound.stop()
                self.ids["search_playback_button_img"].source = "resources/play.png"
            else:
                self.clk = Clock.schedule_interval(self.update_slider, 1)
                self.sound.play()
                self.sound.seek(self.left_of)
                self.ids["search_playback_button_img"].source = "resources/pause.png"


        self.update_labels()

    def start_recording(self):
        state = self.audio.state
        if state == "ready":
            self.audio.start()
        elif state == "recording":
            self.audio.stop()
            home = os.environ["HOME"]
            self.audio_path = f"{home}/Music/audio.wav"
            self.ids["audio_loc"].text = "Ses kaydının adresi: " + str(self.audio_path)
            self.sound = SoundLoader.load(self.audio_path)

        self.update_buttons()
        self.update_labels()

    def update_labels(self):
        record_button = self.ids["record_button"]
        #playback_button = self.ids["playback_button"]
        search_playback_button = self.ids["search_playback_button"]
        audio_upload_button = self.ids["audio_upload"]
        state_label = self.ids["state"]

        recording_state = self.audio.state

        state_label.text = f"Kaydetme Durumu: {self.translate(recording_state)}"

        if recording_state == "ready" and self.sound and not (self.sound.state == "play"): # Ses dosyası var, bekliyoz
            record_button.text = "Kaydetmeye Başla"
            record_button.disabled = False
            search_playback_button.disabled = False
            audio_upload_button.disabled = False

        elif recording_state == "recording": # Kayıt yapılıyo
            record_button.text = "Kaydetmeyi Durdur"
            record_button.disabled = False
            search_playback_button.disabled = True
            audio_upload_button.disabled = True
            
        elif self.sound and self.sound.state == "play": # Kayıt oynatılıyo
            record_button.text = "Kayıt oynatılırken\nses kaydedilemez"
            audio_upload_button.text = "Kayıt oynatılırken\nses yüklenemez"
            record_button.disabled = True
            audio_upload_button.disabled = True
            search_playback_button.disabled = False

    def update_buttons(self):
        if self.sound:
            self.ids["search_playback_button"].disabled = False
            self.ids["process_button"].disabled = False
        
        if self.summary:
            self.ids["search_button"].disabled = False

            if self.template_path:
                self.ids["fill_report_button"].disabled = False

            if self.transcript:
                self.ids["summarize_button"].disabled = False


    def summarize_hf(self):
        if self.audio_path:
            # Convert to mp3
            self.x_to_mp3()
            print("Audio converted to mp3 at:", self.audio_path)
            self.summary, self.transcript, str_form = summarize_hf_tool(self.audio_path)
            self.sentences = list()
            for i in str_form.split("["):
                d = dict()
                data = i.split(",",3)
                d["speaker"], d["start"], d["end"], d["text"] = data
                d["text"] = d["text"].replace("'","")[:-2]
                d["speaker"] = d["speaker"].replace("'","")
                self.sentences.append(d)

            self.ids["summary"].text = self.summary
        self.update_buttons()
        self.save_summary()

    def summarize_gpt(self):
        if self.transcript:
            self.summary = summarize_gpt_tool(self.transcript)
            self.ids["summary"].text = self.summary
        self.update_buttons()
        self.save_summary()

    def save_summary(self):
        doc_name = "resources/Summary_Template.docx"
        tpl=DocxTemplate(doc_name)
        key_info = {"entire_summary": self.summary}
        tpl.render(key_info)
        appointment_time = datetime.now().strftime("%d:%m:%Y-%H_%M_%S")
        tpl.save(f"Summary_{appointment_time}.docx")

        doc_name = "resources/Transcript_Template.docx"
        tpl=DocxTemplate(doc_name)
        key_info = {"entire_transcript": self.transcript}
        tpl.render(key_info)
        appointment_time = datetime.now().strftime("%d:%m:%Y-%H_%M_%S")
        tpl.save(f"Transcript_{appointment_time}.docx")

    def fill_report(self):
        report_filler_tool(self.ids["summary"].text, self.template_path)

    def search_word(self):
        query = self.ids["search_bar"].text
        matches = search_tool(self.sentences, query)

        self.reset_search()
        for i in range(len(matches)):
            if i >= 17:
                break
            d = matches[i]
            start = d["start"]
            end = d["end"]
            text = d["text"]
            button = self.ids[f"search_result_{i}"]
            button.text = f" {str(round(float(start),2))} <-> {str(round(float(end),2))}  -- {text}"  
            button.opacity = 1
            button.disabled = False
                
    def reset_search(self):
        for i in range(17):
            button = self.ids[f"search_result_{i}"]
            button.text = ""
            button.opacity = 0
            button.disabled = True

    def jump_to_sentence(self, button_no):
        button = self.ids[f"search_result_{button_no}"]
        slider = self.ids["view_audio_slider"]

        start_time, _ = button.text.split("<->")
        start_time = float(start_time.strip())
        if self.sound.state == "stop":
            self.play_sound()
        percentage = start_time / self.sound.length
        self.sound.seek(start_time) # self.sound.seek needs a time in seconds
        slider.value = percentage   # slider.value needs a percentage between 0-1

    def x_to_mp3(self):
        audio_suffix = self.audio_path.split(".")[-1]
        if audio_suffix != "mp3":
            old_audio = AudioSegment.from_file(self.audio_path)
            self.audio_path = self.audio_path.replace(audio_suffix,"mp3")
            old_audio.export(self.audio_path, format="mp3")
            self.ids["audio_loc"].text = "Ses kaydının adresi: " + str(self.audio_path)

    def translate(self,sz):
        if sz == "ready":
            return "Hazır"
        elif sz == "recording":
            return "Kaydediyor"
        else:
            return "Bilinmiyor"

    def on_slider_value_change(self, value):
        if self.sound:
            self.sound.seek(value*self.sound.length)
            self.ids["view_audio_slider"].value = value

    def update_slider(self, dt):
        if self.sound and self.sound.state == 'play':
            self.ids["view_audio_slider"].value = self.sound.get_pos()/self.sound.length
            self.ids["timer"].text = time.strftime("%M:%S", time.gmtime(self.sound.get_pos()))

class HealthApp(MDApp):
    def build(self):
        return AudioInterface()
    
if __name__ == "__main__":
    HealthApp().run()