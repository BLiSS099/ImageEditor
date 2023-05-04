import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import ImageTk, Image
from wand.image import Image as wand_img

import os, io

window = tk.Tk()
#window.geometry("1280x720")
class canvasImage:
    def __init__(self):
        self.image = None   #Image to be manipulated (PIL.Image)
        self.image_tk = None #Image to be displayed (PIL.ImageTk.PhotoImage)
        self.preview_image = None #Image for previewing filter

def add_image():
    path = filedialog.askopenfilename(
        initialdir=os.getcwd(),
    )
    canvasImage.image = Image.open(path)
    canvasImage.preview_image = Image.open(path)
    canvasImage.image_tk = ImageTk.PhotoImage(canvasImage.image)
    
    main_canvas.config(width=10, height=10)
    main_canvas.image = ImageTk.PhotoImage(canvasImage.image)
    main_canvas.create_image(0, 0, anchor="nw", image=main_canvas.image)

def add_filter():
    """Challenge1: Due to incompatible variable format of Wand.image and ImageTk.PhotoImage, 
    it is necessary to convert and pass data in bytes format when converting between package"""
    #Convert PIL image to byteIO (blob/bytes)
    buf = io.BytesIO()
    canvasImage.image.save(buf, format="PNG")
    contents = buf.getvalue()

    with wand_img(blob=contents) as img:
        img.blur(radius=3, sigma=3)
        img.format = 'png'

        #Convert wand image to blob(bytes) for ImageTk/Image to read
        blob = img.make_blob()
        canvasImage.image = Image.open(io.BytesIO(blob))
        canvasImage.image_tk = ImageTk.PhotoImage(canvasImage.image)

        main_canvas.image = ImageTk.PhotoImage(canvasImage.image)
        main_canvas.create_image(0, 0, anchor="nw", image=main_canvas.image)

def save_image():
    #save image
    path = filedialog.asksaveasfile(
        initialdir=os.getcwd(),
        initialfile="Untitled.png",
        defaultextension=".png",
        filetypes=[("Image", "*.png")]
    )
    if path:
        os.chdir(os.path.dirname(path.name))
        canvasImage.image.save(path.name)

var = tk.DoubleVar()
def get_value():
    print(var.get())

""" window.columnconfigure(0, weight=1)
window.rowconfigure(0, weight=1) """
""" window.grid_columnconfigure(1, weight=1)
window.grid_columnconfigure(0, weight=0.5)
window.grid_columnconfigure(2, weight=0.5)
window.grid_rowconfigure(0, weight=1) """

window.grid_columnconfigure([5,8], weight=1) #Resize for main_canvas
#window.grid_columnconfigure([0,4], weight=1) #Resize for side_frame_left
#window.grid_columnconfigure([9,12], weight=1) #Resize for side_frame_right
window.rowconfigure(0, weight=1)

#Tips: Use sticky on grid for resizing

main_canvas = tk.Canvas(master=window, height=250, width=850, relief="ridge", borderwidth=4)
main_canvas.grid(row=0, column=5, rowspan=4, columnspan=4, sticky="NESW") 

top_left_frame = tk.Frame(master=window, height=250, width=200, relief="ridge", borderwidth=2)
top_left_frame.grid(row=0, column=0, rowspan=2, columnspan=4, sticky="NSW", padx=1, pady=1) 
top_left_frame.grid_propagate(0)
add_image_btn = tk.Button(top_left_frame, text="add image", relief="raised", padx=10, command=add_image)
add_image_btn.grid(row=0, column=0)
save_image_btn = tk.Button(top_left_frame, text="save image", relief="raised", padx=10, command=save_image)
save_image_btn.grid(row=0, column=1)

top_right_frame = tk.Frame(master=window, height=250, width=200, relief="ridge", borderwidth=2)
top_right_frame.grid(row=0, column=9, rowspan=2, columnspan=4, sticky="NES", padx=1, pady=2)
top_right_frame.grid_propagate(0)
side_frame_addfilter = tk.Button(top_right_frame, text="Add filter", relief="raised", padx=10, command=add_filter)
side_frame_addfilter.grid(row=2, column=1, pady=10, padx=10)

bot_left_frame = tk.Frame(master=window, height=250, width=200, relief="ridge", borderwidth=2)
bot_left_frame.grid(row=2,column=0, rowspan=2, columnspan=4, sticky="NSW", padx=1, pady=1)


bot_right_frame = tk.Frame(master=window, height=250, width=200, relief="ridge", borderwidth=2)
bot_right_frame.grid(row=2, column=9, rowspan=2, columnspan=4, sticky="NES", padx=1, pady=1)
bot_right_frame.grid_propagate(0)
slider = tk.Scale(master=bot_right_frame, from_=0.0, to=5.0, resolution=0.1, orient="horizontal", width=10, length=150, label="Slider", variable=var)
slider.set(2.5)
slider.grid(row=0, column=0, padx=15)


window.mainloop()