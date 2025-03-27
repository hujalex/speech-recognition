import speech_recognition as sr
from pynput import keyboard

recognizer = sr.Recognizer()
is_listening = False
stop_listening = None

def listen_in_background(callback):
    global stop_listening
    stop_listening = recognizer.listen_in_background(sr.Microphone(), callback)


def recognize_callback(recognizer, audio):
    global is_listening
    if is_listening:
        try:
            text = recognizer.recognize_google(audio)
            print("You said: " + text)
        except sr.UnknownValueError:
            print("Speech Recognitino could not understand")
        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition")

def on_key_press(key):
    global is_listening, stop_listening

    if not is_listening and key == keyboard.Key.space:
        print("Start listening... (speak now)")
        is_listening = True

        if stop_listening is None:
            with sr.Microphone() as source:
                print("Adjusting for ambient noise...")
                recognizer.adjust_for_ambient_noise(source, duration = 1)
            listen_in_background(recognize_callback)
    

def on_key_release(key):
    global is_listening

    if key == keyboard.Key.space:
        print("Stopped listening.")
        is_listening = False

    print("Release")
    if key == keyboard.Key.esc:
        global stop_listening
        if stop_listening:
            stop_listening(wait_for_stop = False)
        return False

def key_listener():
    with keyboard.Listener(on_press=on_key_press, on_release=on_key_release) as listener:
        listener.join();



def main():
    print("Press and hold SPACE to listen, ESC to exit.")
    with keyboard.Listener(on_press = on_key_press, on_release = on_key_release) as listener:
        listener.join()


if __name__ == '__main__':
    # main()
    key_listener();