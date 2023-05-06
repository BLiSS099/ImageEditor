import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import ImageTk, Image
from wand.image import Image as wand_img

import os, io

window = tk.Tk()
window.geometry("1280x720")
var = tk.DoubleVar()
class canvasImage:
    def __init__(self):
        self.image = None   #Image to be manipulated (PIL.Image)
        self.preview_image = None #Image for previewing filter 

def resizing(e):
    global width,height
    window.update() #Tkinter root needs to be updated for getting width and height value of main_canvas
    width, height = e.width, e.height
    print(f"Width: {width} Height: {height}")

def add_image():
    path = filedialog.askopenfilename(
       initialdir=os.getcwd(),
    )
    canvasImage.image = Image.open(path)
    canvasImage.preview_image = Image.open(path)
    
    width, height = main_canvas.winfo_width(), main_canvas.winfo_height()
    #main_canvas.image = ImageTk.PhotoImage(canvasImage.preview_image)
    main_canvas.image = ImageTk.PhotoImage(canvasImage.preview_image.resize(
        (int(canvasImage.preview_image.width/1.5), int(canvasImage.preview_image.height/1.5)), 
         resample=Image.LANCZOS
        ))
    main_canvas.create_image(width/2, height/2, anchor="center", image=main_canvas.image)

def add_filter():
    """Challenge1: Due to incompatible variable format of Wand.image and ImageTk.PhotoImage, 
    it is necessary to convert and pass data in bytes format when converting between package"""

    #Convert PIL image to byteIO (blob/bytes)
    buf = io.BytesIO()
    canvasImage.image.save(buf, format="PNG") #Convert original image to blob for preview_image
    contents = buf.getvalue()

    with wand_img(blob=contents) as img:
        img.blur(radius=var.get(), sigma=3)
        img.format = 'png'

        blob = img.make_blob()
        canvasImage.preview_image = Image.open(io.BytesIO(blob)) 
        main_canvas.image = ImageTk.PhotoImage(canvasImage.preview_image.resize(
            (int(canvasImage.preview_image.width/1.5), int(canvasImage.preview_image.height/1.5)), 
            resample=Image.LANCZOS
            ))
        main_canvas.create_image(width/2, height/2, anchor="center", image=main_canvas.image)
    apply_filter_btn["state"] = "normal"

def apply_filter():
    #Apply filter to original image
    canvasImage.image = canvasImage.preview_image
    print("Filter applied!")

def undo_filter():
    #Revert filter and set main_canvas.image to original (canvasImage.image)
    main_canvas.image = ImageTk.PhotoImage(canvasImage.image.resize(
            (int(canvasImage.preview_image.width/1.5), int(canvasImage.preview_image.height/1.5)), 
            resample=Image.LANCZOS
            ))
    main_canvas.create_image(width/2, height/2, anchor="center", image=main_canvas.image)
    apply_filter_btn["state"] = "disabled"
    print("Filter undo-ed!")

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


window.grid_columnconfigure([5,8], weight=1) #Resize for main_canvas
window.rowconfigure([0,2], weight=1)

#Tips: Use sticky on grid for resizing

main_canvas = tk.Canvas(master=window, height=250, width=850, relief="ridge", borderwidth=2)
main_canvas.grid(row=0, column=5, rowspan=4, columnspan=4, sticky="NESW") 

top_left_frame = tk.Frame(master=window, height=250, width=230, relief="ridge", borderwidth=2)
top_left_frame.grid(row=0, column=0, rowspan=2, columnspan=4, sticky="NSW", padx=1, pady=1) 
top_left_frame.grid_propagate(0)
add_image_btn = tk.Button(top_left_frame, text="add image", relief="raised", padx=10, command=add_image)
add_image_btn.grid(row=0, column=0, padx=10, pady=15)
save_image_btn = tk.Button(top_left_frame, text="save image", relief="raised", padx=10, command=save_image)
save_image_btn.grid(row=0, column=1, padx=10, pady=15)

top_right_frame = tk.Frame(master=window, height=250, width=230, relief="ridge", borderwidth=2)
top_right_frame.grid(row=0, column=9, rowspan=2, columnspan=4, sticky="NES", padx=1, pady=2)
top_right_frame.grid_propagate(0)
side_frame_addfilter = tk.Button(top_right_frame, text="Add filter", relief="raised", padx=10, command=add_filter)
side_frame_addfilter.grid(row=2, column=1, pady=10, padx=10)

bot_left_frame = tk.Frame(master=window, height=250, width=230, relief="ridge", borderwidth=2)
bot_left_frame.grid(row=2,column=0, rowspan=2, columnspan=4, sticky="NSW", padx=1, pady=1)

bot_right_frame = tk.Frame(master=window, height=250, width=230, relief="ridge", borderwidth=2)
bot_right_frame.grid(row=2, column=9, rowspan=2, columnspan=4, sticky="NES", padx=1, pady=1)
bot_right_frame.grid_propagate(0)
slider = tk.Scale(master=bot_right_frame, from_=1.0, to_=10.0, resolution=0.1, orient="horizontal", width=10, length=150, label="Slider", variable=var)
slider.set(4.0)
slider.grid(row=0, column=0, padx=15)
apply_filter_btn = tk.Button(master=bot_right_frame, text="Apply filter", relief="raised", command=apply_filter, state="disabled")
apply_filter_btn.grid(row=1, column=0)
undo_btn = tk.Button(master=bot_right_frame, text="Undo", relief="raised", command=undo_filter)
undo_btn.grid(row=2, column=0)

main_canvas.bind("<Configure>", resizing)

window.mainloop()