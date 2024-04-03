# Import required libraries
from tkinter import *
from PIL import ImageTk, Image

# Create an instance of tkinter window
win = Tk()

# Define the geometry of the window
win.geometry("1000x500")

frame = Frame(win, width=1000, height=400)
frame.pack()
frame.place(anchor='center', relx=0.3, rely=0.3)

# Create an object of tkinter ImageTk
img = ImageTk.PhotoImage(Image.open("stitched_image_without_pillow2.png"))

# Create a Label Widget to display the text or Image
label = Label(frame, image = img)
label.pack()

win.mainloop()