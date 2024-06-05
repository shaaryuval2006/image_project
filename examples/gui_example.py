from tkinter import *
import tkinter as tk


def register():
    pass

def sign_in():
    pass


base = tk.Tk()
base.geometry('600x400')
button1 = tk.Button(base, text="Register", command=register, height = 3, width = 10, bg='lightblue')
button1.place(relx = 0.3,
                   rely = 0.3)
button2 = tk.Button(base, text="sign-in", command=sign_in, height = 3, width = 10, bg='lightgreen')
button2.place(relx = 0.6,
                   rely = 0.3)


mainloop()
