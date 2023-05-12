import os
import io
import urllib.request

import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox

from PIL import ImageTk, Image, UnidentifiedImageError, ImageOps
from wand.image import Image as wand_img



window = tk.Tk()
window.geometry("1280x720")
var = tk.DoubleVar()
class canvasImage:
    def __init__(self):
        self.image = None   #Image to be manipulated (PIL.Image)
        self.preview_image = None #Image for previewing filter 

def download():
    url = simpledialog.askstring("URL", "Paste URL here")
    try:
        urllib.request.urlretrieve(url, "picture.png")
        canvasImage.image = Image.open("picture.png")
        canvasImage.preview_image = Image.open("picture.png")
        
        width, height = main_canvas.winfo_width(), main_canvas.winfo_height()
        main_canvas.image = ImageTk.PhotoImage(canvasImage.preview_image.resize(
            (int(canvasImage.preview_image.width/1.5), int(canvasImage.preview_image.height/1.5)), 
            resample=Image.LANCZOS
            ))
        main_canvas.create_image(canvas_width/2, canvas_height/2, anchor="center", image=main_canvas.image)
    except UnidentifiedImageError:
        print("Invalid image url")

def resizing(e):
    global canvas_width, canvas_height
    window.update() #Tkinter root needs to be updated for getting width and height value of main_canvas
    canvas_width, canvas_height = e.width, e.height
    print(f"Width: {canvas_width} Height: {canvas_height}")

def add_image():
    path = filedialog.askopenfilename(
       initialdir=os.getcwd(),
    )
    canvasImage.image = Image.open(path)
    canvasImage.preview_image = Image.open(path)
    
    width, height = main_canvas.winfo_width(), main_canvas.winfo_height()
    main_canvas.image = ImageTk.PhotoImage(canvasImage.preview_image.resize(
        (int(canvasImage.preview_image.width/1.5), int(canvasImage.preview_image.height/1.5)), 
         resample=Image.LANCZOS
        ))
    main_canvas.create_image(canvas_width/2, canvas_height/2, anchor="center", image=main_canvas.image)

#Image transform functions
def transform(method):
    canvasImage.preview_image = method(canvasImage.preview_image)
    canvasImage.image = canvasImage.preview_image

    width, height = main_canvas.winfo_width(), main_canvas.winfo_height()
    main_canvas.image = ImageTk.PhotoImage(canvasImage.preview_image.resize(
        (int(canvasImage.preview_image.width/1.5), int(canvasImage.preview_image.height/1.5)), 
         resample=Image.LANCZOS
        ))
    main_canvas.create_image(canvas_width/2, canvas_height/2, anchor="center", image=main_canvas.image)

def flip(img):
    return ImageOps.flip(img)

def mirror(img):
    return ImageOps.mirror(img)

def rotate(img):
    return img.rotate(90)
    
#Image effects functions
def noise(img):
    img.noise("gaussian", attenuate=1.0)
    img.format = 'png'

def charcoal(img):
    img.charcoal(radius=1.5, sigma=0.5)
    img.format = 'png'

def blur(img):
    img.blur(radius=var.get(), sigma=3)

def add_effects(image_effect): #Passing image effects functions as parameters
    """Challenge1: Due to incompatible variable format of Wand.image and ImageTk.PhotoImage, 
    it is necessary to convert and pass data in bytes format when converting between package"""
    
    #Convert PIL image to byteIO (blob/bytes)
    buf = io.BytesIO()
    canvasImage.image.save(buf, format="PNG")
    contents = buf.getvalue()

    with wand_img(blob=contents) as img:
        image_effect(img) #Add image effects to preview_image
        img.format = 'png'

        blob = img.make_blob()
        canvasImage.preview_image = Image.open(io.BytesIO(blob)) 
        main_canvas.image = ImageTk.PhotoImage(canvasImage.preview_image.resize(
            (int(canvasImage.preview_image.width/1.5), int(canvasImage.preview_image.height/1.5)), 
            resample=Image.LANCZOS
            ))
        main_canvas.create_image(canvas_width/2, canvas_height/2, anchor="center", image=main_canvas.image)
    apply_filter_btn["state"] = "normal"

def apply_effects():
    #Applying effects to original image (canvasImage.image)
    canvasImage.image = canvasImage.preview_image
    print("Filter applied!")

def undo_effects():
    #Revert filter and set main_canvas.image to original (canvasImage.image)
    main_canvas.image = ImageTk.PhotoImage(canvasImage.image.resize(
            (int(canvasImage.preview_image.width/1.5), int(canvasImage.preview_image.height/1.5)), 
            resample=Image.LANCZOS
            ))
    main_canvas.create_image(canvas_width/2, canvas_height/2, anchor="center", image=main_canvas.image)
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

#Tips: Use sticky on grid for resizing

main_canvas = tk.Canvas(master=window, height=250, width=850, relief="ridge", borderwidth=2)
main_canvas.grid(row=0, column=5, rowspan=4, columnspan=4, sticky="NESW") 

top_left_frame = tk.Frame(master=window, height=250, width=250, relief="ridge", borderwidth=2)
top_left_frame.grid(row=0, column=0, rowspan=2, columnspan=4, sticky="NSW", padx=1, pady=1) 
top_left_frame.grid_propagate(0)

add_image_label = tk.Label(top_left_frame, text="Local Computer : ")
add_image_btn = tk.Button(top_left_frame, text="Add image", relief="raised", padx=10, command=add_image)
or_label = tk.Label(top_left_frame, text="OR")
url_submit_label = tk.Label(top_left_frame, text="URL Download : ")
url_submit_btn = tk.Button(top_left_frame, text="Download", relief="raised", padx=10, command=download)
save_image_btn = tk.Button(top_left_frame, text="Save image", relief="raised", padx=10, command=save_image)

url_submit_label.grid(row=0, column=0, padx=20, pady=5)
or_label.grid(row=1, column=0, columnspan=2, pady=5)
url_submit_btn.grid(row=0, column=1, padx=20, pady=5)
add_image_label.grid(row=2, column=0, padx=5, pady=5)
add_image_btn.grid(row=2, column=1, padx=10, pady=5)
save_image_btn.grid(row=3, column=1, padx=10, pady=20)

top_right_frame = tk.Frame(master=window, height=250, width=250, relief="ridge", borderwidth=2)
top_right_frame.grid(row=0, column=9, rowspan=2, columnspan=4, sticky="NES", padx=1, pady=2)
top_right_frame.grid_propagate(0)

blur_btn = tk.Button(top_right_frame, text="Blur", relief="raised", padx=10, command=lambda: add_effects(blur))
noise_btn = tk.Button(top_right_frame, text="Noise", relief="raised", padx=10, command=lambda: add_effects(noise))
charcoal_btn = tk.Button(top_right_frame, text="Charcoal", relief="raised", padx=10, command=lambda: add_effects(charcoal))

blur_btn.grid(row=2, column=1, padx=5, pady=10)
noise_btn.grid(row=2, column=2, padx=5, pady=10)
charcoal_btn.grid(row=2, column=3, padx=5, pady=10)

bot_left_frame = tk.Frame(master=window, height=250, width=250, relief="ridge", borderwidth=2)
bot_left_frame.grid(row=2,column=0, rowspan=2, columnspan=4, sticky="NSW", padx=1, pady=1)
bot_left_frame.grid_propagate(0)

transform_label = tk.Label(master=bot_left_frame, text="Transform Image")
transform_label.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="W")
flip_btn = tk.Button(master=bot_left_frame, text="Flip", relief="raised", width=7,command=lambda: transform(flip))
flip_btn.grid(row=1, column=0, padx=10, pady=5)
mirror_btn = tk.Button(master=bot_left_frame, text="Mirror", relief="raised", width=7, command=lambda: transform(mirror))
mirror_btn.grid(row=1, column=1, padx=10, pady=5)
rotate_btn = tk.Button(master=bot_left_frame, text="Rotate", relief="raised", width=7, command=lambda: transform(rotate))
rotate_btn.grid(row=1, column=2, padx=10, pady=5)

bot_right_frame = tk.Frame(master=window, height=250, width=250, relief="ridge", borderwidth=2)
bot_right_frame.grid(row=2, column=9, rowspan=2, columnspan=4, sticky="NES", padx=1, pady=1)
bot_right_frame.grid_propagate(0)

slider = tk.Scale(master=bot_right_frame, from_=1.0, to_=20.0, resolution=0.1, orient="horizontal", width=10, length=150, label="Slider", variable=var)
slider.set(6.0)
apply_filter_btn = tk.Button(master=bot_right_frame, text="Apply filter", relief="raised", command=apply_effects, state="disabled")
undo_btn = tk.Button(master=bot_right_frame, text="Undo", relief="raised", command=undo_effects)

apply_filter_btn.grid(row=1, column=0)
slider.grid(row=0, column=0, padx=15)
undo_btn.grid(row=1, column=1)

main_canvas.bind("<Configure>", resizing)
window.grid_columnconfigure([5,8], weight=1) #Resize for main_canvas
window.rowconfigure([0,2], weight=1) #Resize rows

window.mainloop()