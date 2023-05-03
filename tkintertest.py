import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import ImageTk, Image
from wand.image import Image as wand_img

import os, io

window = tk.Tk()
window.geometry("1280x720")
class canvasImage:
    def __init__(self):
        self.image = None   #Image to be manipulated (PIL.Image)
        self.image_tk = None #Image to be displayed (PIL.ImageTk.PhotoImage)

def add_image():
    path = filedialog.askopenfilename(
        initialdir=os.getcwd(),
    )
    canvasImage.image = Image.open(path)
    canvasImage.image_tk = ImageTk.PhotoImage(canvasImage.image)
    
    main_canvas.config(width=10, height=10)
    main_canvas.image = ImageTk.PhotoImage(canvasImage.image)
    main_canvas.create_image(0, 0, anchor="nw", image=main_canvas.image)

def add_filter():
    """Challenge1: Due to incompatible variable format of Wand.image and ImageTk.PhotoImage, 
    it is necessary to convert and pass data in bytes format to each package"""
    #Convert PIL image to byteIO (blob/bytes)
    buf = io.BytesIO()
    canvasImage.image.save(buf, format="PNG")
    contents = buf.getvalue()

    with wand_img(blob=contents) as img:
        img.blur(radius=0, sigma=3)
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
        

window.grid_columnconfigure(0, weight=1)
window.grid_rowconfigure(0, weight=1)

#Tips: Use sticky on grid for resizing

main_canvas = tk.Canvas(master=window, height=250, width=500, relief="ridge", borderwidth=4)
main_canvas.grid(row=0, column=0, rowspan=3, columnspan=3, sticky="nesw")

bot_nav_bar = tk.Frame(window, relief="raised", borderwidth=2, width=500, height=50)
add_image_btn = tk.Button(bot_nav_bar, text="add image", relief="raised", padx=10, command=add_image)
add_image_btn.grid(row=0, column=0)
save_image_btn = tk.Button(bot_nav_bar, text="save image", relief="raised", padx=10, command=save_image)
save_image_btn.grid(row=0, column=1)
bot_nav_bar.grid(row=4, column=0, rowspan=2, columnspan=6, sticky="esw")
bot_nav_bar.grid_propagate(0)

side_frame = tk.Frame(window, width=200, height=250, relief="ridge", borderwidth=2)
side_frame.grid(row=0, column=4, rowspan=3 , columnspan=3, sticky="nes")
side_frame.grid_propagate(0)
side_frame_addfilter = tk.Button(side_frame, text="Add filter", relief="raised", padx=10, command=add_filter)
side_frame_addfilter.grid(row=2, column=1, pady=10, padx=10)

window.mainloop()