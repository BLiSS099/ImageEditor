import os
import io
import requests

import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox, ttk

from PIL import ImageTk, Image, UnidentifiedImageError, ImageOps
from wand.image import Image as wand_img

window = tk.Tk()
window.geometry("1280x720")
window.title("Wand Image Editor")

class canvasImage:
    def __init__(self):
        self.image = None   #Image to be manipulated (PIL.Image)
        self.preview_image = None #Image for previewing filter 

#Allow resizing of image on main canvas
def resizing(e):
    global canvas_width, canvas_height
    window.update() #Tkinter root needs to be updated for getting width and height value of main_canvas
    canvas_width, canvas_height = e.width, e.height
    print(f"Width: {canvas_width} Height: {canvas_height}")

#Render image on main_canvas
def render_image(img):
    main_canvas.image = ImageTk.PhotoImage(img.resize(
            (int(img.width/1.5), int(img.height/1.5)), 
            resample=Image.LANCZOS
            ))
    main_canvas.create_image(canvas_width/2, canvas_height/2, anchor="center", image=main_canvas.image)

#Download image from URL
def download():
    url = simpledialog.askstring("URL", "Paste URL here")
    try:
        img = requests.get(url)
        canvasImage.image = Image.open(io.BytesIO(img.content))
        canvasImage.preview_image = Image.open(io.BytesIO(img.content))
        render_image(canvasImage.preview_image)

    except UnidentifiedImageError:
        print("Invalid image url")

def add_image():
    path = filedialog.askopenfilename(
       initialdir=os.getcwd(),
    )
    canvasImage.image = Image.open(path)
    canvasImage.preview_image = Image.open(path)

    render_image(canvasImage.preview_image)

#Image transform functions
def transform(method):
    canvasImage.preview_image = method(canvasImage.preview_image)
    canvasImage.image = canvasImage.preview_image
    render_image(canvasImage.preview_image)

def flip(img):
    return ImageOps.flip(img)

def mirror(img):
    return ImageOps.mirror(img)

def rotate(img):
    return img.rotate(90, expand=True)
    
#Image effects functions
def noise(img):
    img.noise(options_type.get(), attenuate=options_attenuate.get())

def charcoal(img):
    img.charcoal(radius=options_radius.get(), sigma=options_sigma.get())

def blur(img):
    img.blur(radius=options_radius.get(), sigma=options_sigma.get())

def edge(img):
    img.transform_colorspace('gray')
    img.edge(radius=options_radius.get())

def blueshift(img):
    img.blue_shift(factor=options_factor.get())

def kuwahara(img):
    img.kuwahara(radius=options_radius.get(), sigma=options_sigma.get())

def sepia(img):
    img.sepia_tone(threshold=options_threshold.get())

#Filter list to be displayed in widgets
effects_list = {
    'Blur': blur,
    'Noise': noise,
    'Charcoal': charcoal,
    'Edge': edge,
    'Blue Shift': blueshift,
    'Kuwahara': kuwahara,
    'Sepia Tone': sepia
} 

def add_effects(image_effect): #Passing image effects functions as parameters
    """Due to incompatible variable format of Wand.image and ImageTk.PhotoImage, 
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
        render_image(canvasImage.preview_image)
    apply_effect_btn["state"] = "normal"

def apply_effects():
    #Applying effects to original image (canvasImage.image)
    canvasImage.image = canvasImage.preview_image
    print("Filter applied!")

def undo_effects():
    #Revert filter and set main_canvas.image to original (canvasImage.image)
    render_image(canvasImage.image)
    apply_effect_btn["state"] = "disabled"
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


"""Declaring tkinter variables for accessing widget values in each options"""
options_radius = tk.DoubleVar() #Radius value (slider widget)
options_attenuate = tk.DoubleVar() #Attenuate value (slider widget)
options_sigma = tk.DoubleVar() #Sigma value (slider widget)
options_factor = tk.DoubleVar() #Factor vlaue (slider widget)
options_threshold = tk.DoubleVar() #Threshold value (slider widget)
options_type = tk.StringVar() #For accessing selected effect type

def blur_options():
    title = tk.Label(bot_right_frame, text="Blur Options")
    radius = tk.Scale(bot_right_frame, from_=1.0, to_=10.0, resolution=0.5, orient="horizontal", 
                      width=10, length=200,label="Radius", variable=options_radius, relief="ridge", borderwidth=2)
    radius.set(5.0)
    sigma = tk.Scale(bot_right_frame, from_=0.0, to_=5.0, resolution=0.1, orient="horizontal", 
                      width=10, length=200,label="Attenuate", variable=options_sigma, relief="ridge", borderwidth=2)
    sigma.set(2.0)

    title.grid(row=0, column=0,padx=5, pady=5, sticky="w")
    radius.grid(row=1, column=0, columnspan=2, padx=5, pady=5)
    sigma.grid(row=2, column=0, columnspan=2, padx=5, pady=5)
    return(title, radius, sigma)

def blueshift_options():
    title = tk.Label(bot_right_frame, text="Blur Options")
    factor = tk.Scale(bot_right_frame, from_=1.0, to_=2.0, resolution=0.01, orient="horizontal", 
                      width=10, length=200,label="Factor", variable=options_factor, relief="ridge", borderwidth=2)
    factor.set(1.20)

    title.grid(row=0, column=0,padx=5, pady=5, sticky="w")
    factor.grid(row=1, column=0, columnspan=2, padx=5, pady=5)
    return(title, factor)

def noise_options():
    noise_list = [
        'gaussian',
        'impulse',
        'laplacian',
        'multiplicative_gaussian',
        'poisson',
        'random',
        'uniform'
    ]
    noise_type = ttk.OptionMenu(
        bot_right_frame,
        options_type,
        "Select a type",
        *noise_list
    )
    title = tk.Label(bot_right_frame, text="Noise effect options")
    noise_type_label = tk.Label(bot_right_frame, text="Filter type :")
    attenuate = tk.Scale(bot_right_frame, from_=0.0, to_=3.0, resolution=0.1, orient="horizontal", 
                      width=10, length=200,label="Attenuate", variable=options_attenuate, relief="ridge", borderwidth=2)
    attenuate.set(1.0)

    title.grid(row=0, column=0, padx=5, pady=5, sticky="w")
    noise_type_label.grid(row=1, column=0, pady=5)
    noise_type.grid(row=1, column=1, columnspan=2, pady=5, sticky="w")
    attenuate.grid(row=2, column=0, columnspan=2, padx=5, pady=5)
    return(title, attenuate, noise_type)

def charcoal_options():
    title = tk.Label(bot_right_frame, text="Charcoal effect options")
    radius = tk.Scale(bot_right_frame, from_=1.0, to_=8.0, resolution=0.01, orient="horizontal", 
                      width=10, length=200,label="Radius", variable=options_radius, relief="ridge", borderwidth=2)
    radius.set(2.0)
    sigma = tk.Scale(bot_right_frame, from_=0.0, to_=5.0, resolution=0.1, orient="horizontal", 
                      width=10, length=200,label="Sigma", variable=options_sigma, relief="ridge", borderwidth=2)
    sigma.set(2.0)

    title.grid(row=0, column=0,padx=5, pady=5, sticky="w")
    radius.grid(row=1, column=0, columnspan=2, padx=5, pady=5)
    sigma.grid(row=2, column=0, columnspan=2, padx=5, pady=5)
    return(title, radius, sigma)

def edge_options():
    title = tk.Label(bot_right_frame, text="Edge effect options")
    radius = tk.Scale(bot_right_frame, from_=1.0, to_=10.0, resolution=1.0, orient="horizontal", 
                      width=10, length=200,label="Radius", variable=options_radius, relief="ridge", borderwidth=2)
    radius.set(1.0)

    title.grid(row=0, column=0,padx=5, pady=5, sticky="w")
    radius.grid(row=1, column=0, columnspan=2, padx=5, pady=5)
    return(title, radius)

def kuwahara_options():
    title = tk.Label(bot_right_frame, text="Kuwahara effect options")
    radius = tk.Scale(bot_right_frame, from_=1.0, to_=8.0, resolution=0.01, orient="horizontal", 
                      width=10, length=200,label="Radius", variable=options_radius, relief="ridge", borderwidth=2)
    radius.set(2.0)
    sigma = tk.Scale(bot_right_frame, from_=0.0, to_=5.0, resolution=0.1, orient="horizontal", 
                      width=10, length=200,label="Sigma", variable=options_sigma, relief="ridge", borderwidth=2)
    sigma.set(2.0)

    title.grid(row=0, column=0, padx=5, pady=5, sticky="w")
    radius.grid(row=1, column=0, columnspan=2, padx=5, pady=5)
    sigma.grid(row=2, column=0, columnspan=2, padx=5, pady=5)
    return(title, radius, sigma)

def sepia_options():
    title = tk.Label(bot_right_frame, text="Sepia Tone effect options")
    threshold = tk.Scale(bot_right_frame, from_=0.1, to_=1.0, resolution=0.01, orient="horizontal", 
                      width=10, length=200,label="Threshold", variable=options_threshold, relief="ridge", borderwidth=2)
    threshold.set(0.5)

    title.grid(row=0, column=0, padx=5, pady=5, sticky="w")
    threshold.grid(row=1, column=0, columnspan=2, padx=5, pady=5)
    return(title, threshold)

options_widgets = {
    "Blur": blur_options,
    "Noise": noise_options,
    "Charcoal": charcoal_options,
    "Edge": edge_options,
    "Blue Shift": blueshift_options,
    "Kuwahara": kuwahara_options,
    "Sepia Tone": sepia_options
}

def render_widget(key):
    for widget in bot_right_frame.winfo_children():
        widget.destroy()

    selected_filter = options_widgets[key] #Select function value from widgets dict
    print(f"Rendering: {selected_filter}")
    selected_filter() #Run the function and render widgets for selected options

""" Tkinter GUI code """
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

url_submit_label.grid(row=0, column=0, padx=20, pady=10)
url_submit_btn.grid(row=0, column=1, padx=20, pady=10)
or_label.grid(row=1, column=0, columnspan=2, pady=5)
add_image_label.grid(row=2, column=0, padx=5, pady=5)
add_image_btn.grid(row=2, column=1, padx=10, pady=5)
save_image_btn.grid(row=3, column=1, padx=10, pady=20)

top_right_frame = tk.Frame(master=window, height=250, width=250, relief="ridge", borderwidth=2)
top_right_frame.grid(row=0, column=9, rowspan=2, columnspan=4, sticky="NES", padx=1, pady=2)
top_right_frame.grid_propagate(0)
top_right_frame.rowconfigure(1, weight=1) #Allows second row of the frame to stick to bottom

effects_var = tk.StringVar()
image_effects = ttk.OptionMenu(
    top_right_frame,
    effects_var,
    "Select an effect",
    *effects_list.keys(),
    command=render_widget
)
effects_label = tk.Label(top_right_frame, text="Image effects :")
preview_effect_btn = tk.Button(top_right_frame, text="Preview effect", relief="raised", command=lambda: add_effects(effects_list[effects_var.get()]))
apply_effect_btn = tk.Button(top_right_frame, text="Apply effect", relief="raised", command=apply_effects, state="disabled")
undo_btn = tk.Button(top_right_frame, text="Undo", relief="raised", command=undo_effects)

effects_label.grid(row=0, column=0, padx=5, pady=10)
image_effects.grid(row=0, column=1, columnspan=3, padx=5, pady=10)
preview_effect_btn.grid(row=1, column=0, padx=5, pady=5, sticky="ws")
apply_effect_btn.grid(row=1, column=1, padx=5, pady=5, sticky="s")
undo_btn.grid(row=1, column=2, padx=5, pady=5, sticky="es")

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

bot_right_frame = tk.Frame(window, height=250, width=250, relief="ridge", borderwidth=2)
bot_right_frame.grid(row=2, column=9, rowspan=2, columnspan=4, sticky="NES", padx=1, pady=1)
bot_right_frame.grid_propagate(0)

label = tk.Label(bot_right_frame, text="Options Menu")
label.grid(row=0, column=0, padx=5, pady=5)

main_canvas.bind("<Configure>", resizing)
window.grid_columnconfigure([5,8], weight=1) #Resize for main_canvas
window.rowconfigure([0,2], weight=1) #Resize rows

window.mainloop()
