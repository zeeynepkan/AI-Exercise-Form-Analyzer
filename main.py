# main.py   masaüstü veri toplama arayüzü 

import tkinter as tk
from tkinter import messagebox
from modules.data_collector import DataCollector
from config import Config

collector = DataCollector()


def start_collection():


    exercise_type = exercise_var.get()
    label_text = label_var.get()


    if label_text == "Doğru":
        form_label = 1
    else:
        form_label = 0

    try:
        duration = int(duration_entry.get())
    except ValueError:
        messagebox.showerror("Hata", "Süre sayı olmalıdır!")
        return

    messagebox.showinfo(
        "Başlıyor",
        f"{exercise_type} veri toplama başlıyor!"
    )


    collector.collect_from_webcam(
        exercise_type=exercise_type,
        form_label=form_label,
        duration_seconds=duration
    )



# Ana pencere
root = tk.Tk()
root.title("Exercise Form Analyzer")
root.geometry("400x400")
root.configure(bg="white")


# Başlık
title = tk.Label(
    root,
    text="Exercise Form Analyzer",
    font=("Arial", 18, "bold"),
    bg="white"
)

title.pack(pady=20)


# Egzersiz seçimi
exercise_label = tk.Label(
    root,
    text="Egzersiz Seç",
    font=("Arial", 11),
    bg="white"
)

exercise_label.pack()

exercise_var = tk.StringVar(value="squat")

exercise_menu = tk.OptionMenu(
    root,
    exercise_var,
    *Config.EXERCISE_TYPES
)

exercise_menu.pack(pady=10)


# Form etiketi
label_title = tk.Label(
    root,
    text="Form Tipi",
    font=("Arial", 11),
    bg="white"
)

label_title.pack()

label_var = tk.StringVar(value="Doğru")

label_menu = tk.OptionMenu(
    root,
    label_var,
    "Doğru",
    "Yanlış"
)

label_menu.pack(pady=10)


# Süre
duration_label = tk.Label(
    root,
    text="Süre (saniye)",
    font=("Arial", 11),
    bg="white"
)

duration_label.pack()

duration_entry = tk.Entry(root, justify="center")
duration_entry.insert(0, "10")
duration_entry.pack(pady=10)


# BAŞLAT BUTONU
start_button = tk.Button(
    root,
    text="▶ Veri Toplamayı Başlat",
    command=start_collection,
    bg="#4CAF50",
    fg="white",
    font=("Arial", 12, "bold"),
    width=25,
    height=2
)


start_button.pack(pady=30)


# Bilgi yazısı
info_label = tk.Label(
    root,
    text="Çıkmak için webcam ekranında q tuşuna bas.",
    font=("Arial", 9),
    fg="gray",
    bg="white"
)



info_label.pack()



root.mainloop()