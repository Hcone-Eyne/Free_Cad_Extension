# importing required lib
import speech_recognition as sp
from voice_input.Keys.config import logs_location

# initialising listener
class The_listener:
    def __init__(self):
        self.recognizer = sp.Recognizer() # process the audio data, contains algorithm needs to understand speech
        self.microphone = sp.Microphone() # acessing microphone

    def listen(self):
        # writes what user told in voice_input / opens mic in short words
        with self.microphone as voice_input:
            self.recognizer.adjust_for_ambient_noise(voice_input, duration= 0.5) # adjust sounds / environment based on surrounding sound and duration sets how long it listens for noise 0.5 is faster 2 is more calibraite but slower

            # silent threshold this decide how long must be present to end a phraase
            self.recognizer.pause_threshold = 1 # lower value =Phil is more eager to listen 
            print("Listening.....")
            
            # listen for user to stop
            try:
                # setting pharase_time_limit and timeout
                # phrase_time_limit = max duration of total speech segment
                # timeout = max duration to wait for speech before assuming user is done 
                audio = self.recognizer.listen(
                    voice_input,
                    timeout = 5,
                    phrase_time_limit = 10
                )
            except sp.WaitTimeoutError:
                print("Phil is waiting for you to speak...")
                return None

        # after this the  microphone is closed
        try:
            # using google api to get answer (mac dict is complex as its based on objective C )
            text = self.recognizer.recognize_google(audio)
            print("You said : ", text)
            return text 
        # handles error if user voice isn't clear
        except sp.UnknownValueError:
            print("Phil can't understand the audio ")
            return None
        # handles error if connection is lost or api is down
        except sp.RequestError as e:
            print(f"couldn't process requests from google:{e}")
            return None
        # handles rest of errors
        except Exception as e:
            print("Error:", e)
            # save in syntax file
            with open(logs_location / "error.report.txt", "a") as report:
                report.write(f"Error: {e}\n")
            return None

