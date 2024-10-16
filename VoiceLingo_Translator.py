import tkinter as tk
from tkinter import messagebox, simpledialog, font
import speech_recognition as sr
from googletrans import Translator, LANGUAGES
from pymongo import MongoClient
from PIL import Image, ImageTk

# Create a recognizer and translator instance
recognizer = sr.Recognizer()
translator = Translator()

# MongoDB setup
try:
    client = MongoClient('mongodb://localhost:27017/')  
    db = client['VoiceLingoDB']  # Connect to the database
    translations_collection = db['translations']  # Connect to the collection
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    messagebox.showerror("Database Error", f"Error connecting to MongoDB: {e}")

def save_translation(input_text, input_language, translated_text, target_language):
    translation_data = {
        "input_text": input_text,
        "input_language": input_language,
        "translated_text": translated_text,
        "target_language": target_language
    }
    try:
        translations_collection.insert_one(translation_data)
        print("Translation saved to MongoDB.")
    except Exception as e:
        print(f"Error saving translation to MongoDB: {e}")
        messagebox.showerror("Database Error", f"Error saving translation to MongoDB: {e}")

def retrieve_translations():
    try:
        translations = translations_collection.find()
        output_text.insert(tk.END, "Saved Translations:\n\n", "output")
        for translation in translations:
            output_text.insert(tk.END, f"{translation['input_text']} ({LANGUAGES.get(translation['input_language'], 'Unknown Language')}) -> {translation['translated_text']} ({LANGUAGES.get(translation['target_language'], 'Unknown Language')})\n\n", "output")
    except Exception as e:
        print(f"Error retrieving translations from MongoDB: {e}")
        messagebox.showerror("Database Error", f"Error retrieving translations from MongoDB: {e}")

def listen_speech():
    microphone_button.config(text="Listening...", state=tk.DISABLED)
    root.update()
    output_text.delete("1.0", tk.END)

    try:
        with sr.Microphone() as source:
            print("Speak something...")
            audio = recognizer.listen(source)

            user_input = recognizer.recognize_google(audio)
            if user_input:
                input_language = translator.detect(user_input).lang
                if isinstance(input_language, list):
                    input_language = input_language[-1]

                output_text.insert(tk.END, f"You said: {user_input} in {LANGUAGES.get(input_language, 'Unknown Language')}\n\n", "input")

                target_language = simpledialog.askstring("Select Language", "Enter the language code to translate into (e.g., 'en' for English, 'fr' for French):")

                if target_language and target_language != input_language:
                    translated_text = translator.translate(user_input, src=input_language, dest=target_language).text
                    output_text.insert(tk.END, f"Translated to {LANGUAGES.get(target_language, 'Unknown Language')}: {translated_text}\n\n", "output")
                    save_translation(user_input, input_language, translated_text, target_language)
                else:
                    output_text.insert(tk.END, "No translation needed (same language or invalid target language).\n\n", "warning")

    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio.")
        messagebox.showwarning("Speech Recognition Error", "Google Speech Recognition could not understand audio.")
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition; {e}")
        messagebox.showerror("Speech Recognition Error", f"Could not request results from Google Speech Recognition: {e}")

    microphone_button.config(text="Start Microphone", state=tk.NORMAL)
    root.update()

def translate_text():
    input_text = input_text_entry.get("1.0", "end-1c")
    if input_text:
        input_language = translator.detect(input_text).lang
        if isinstance(input_language, list):
            input_language = input_language[-1]

        output_text.insert(tk.END, f"Input text: {input_text} in {LANGUAGES.get(input_language, 'Unknown Language')}\n\n", "input")

        target_language = simpledialog.askstring("Select Language", "Enter the language code to translate into (e.g., 'en' for English, 'fr' for French):")

        if target_language and target_language != input_language:
            translated_text = translator.translate(input_text, src=input_language, dest=target_language).text
            output_text.insert(tk.END, f"Translated to {LANGUAGES.get(target_language, 'Unknown Language')}: {translated_text}\n\n", "output")
            save_translation(input_text, input_language, translated_text, target_language)
        else:
            output_text.insert(tk.END, "No translation needed (same language or invalid target language).\n\n", "warning")
    else:
        messagebox.showwarning("Warning", "Please enter some text to translate.")

# Create the main application window
root = tk.Tk()
root.title("VoiceLingo - Language Translator")
root.geometry("900x700")

# Load and set the background image
try:
    bg_image = Image.open("trans2.jpg")
    bg_image = bg_image.resize((900, 700), Image.LANCZOS)
    bg_photo = ImageTk.PhotoImage(bg_image)
    bg_label = tk.Label(root, image=bg_photo)
    bg_label.place(relwidth=1, relheight=1)
except Exception as e:
    print(f"Error loading background image: {e}")
    messagebox.showerror("Image Error", f"Error loading background image: {e}")

# Create a custom font for the title
title_font = font.Font(family="Arial", size=24, weight="bold")

# Create a welcome label with custom font and styling
welcome_label = tk.Label(root, text="Welcome to VoiceLingo - A Language Translator", font=title_font, bg="#ADADAD", fg="#0066cc")
welcome_label.pack(pady=20)

# Create a frame for the input text entry and button with custom styling
input_frame = tk.Frame(root, bg="#f0f0f0", bd=5, relief=tk.GROOVE)
input_frame.pack(pady=10)
input_text_entry = tk.Text(input_frame, height=5, width=50, font=("Arial", 12), bg="#ffffff", fg="#333333")
input_text_entry.pack(side=tk.LEFT, padx=10)
translate_button = tk.Button(input_frame, text="Translate Text", command=translate_text, font=("Arial", 12), bg="#4CAF50", fg="#FFFFFF", relief=tk.RAISED, borderwidth=2)
translate_button.pack(side=tk.LEFT, padx=10)

# Create a frame for the microphone button with custom styling
microphone_frame = tk.Frame(root, bg="cyan", bd=5, relief=tk.GROOVE)
microphone_frame.pack(pady=10)
microphone_button = tk.Button(microphone_frame, text="Start Microphone", command=listen_speech, font=("Arial", 12), bg="#2196F3", fg="#BFEFFF", relief=tk.RAISED, borderwidth=2)
microphone_button.pack()

# Create a button to retrieve saved translations
retrieve_button = tk.Button(root, text="Retrieve Translations", command=retrieve_translations, font=("Arial", 12), bg="#CD6889", fg="#FFFFFF", relief=tk.RAISED, borderwidth=2)
retrieve_button.pack(pady=30)

# Configure the output text widget with custom styling
output_text = tk.Text(root, height=10, width=50, font=("Arial", 12), bg="#FFFFFF", fg="#333333", relief=tk.SUNKEN, borderwidth=2)
output_text.tag_configure("input", foreground="Purple")
output_text.tag_configure("output", foreground="green")
output_text.tag_configure("warning", foreground="red")
output_text.pack(pady=10)

root.mainloop()
