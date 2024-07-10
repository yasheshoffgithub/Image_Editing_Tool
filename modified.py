import tkinter as tk
from tkinter import filedialog, colorchooser, messagebox
from PIL import Image, ImageOps, ImageTk, ImageFilter, ImageDraw
from tkinter import ttk

root = tk.Tk()
root.geometry("1000x600")
root.title("Image Drawing Tool")
root.config(bg="white")

pen_color = "black"
pen_size = 5
filepath = ""
undo_stack = []
redo_stack = []
image = None
canvas_image = None
start_x = start_y = end_x = end_y = None
angle = 0

original_image = None
current_image = None

is_cropping = False
drawing_enabled = False  # To control drawing state

def add_image():
    global filepath, original_image, current_image
    filepath = filedialog.askopenfilename(initialdir=r"C:\Users\sarik\Desktop")
    if filepath:
        original_image = Image.open(filepath)
        width, height = int(original_image.width / 2), int(original_image.height / 2)
        original_image = original_image.resize((width, height), Image.LANCZOS)
        current_image = original_image.copy()
        undo_stack.append(current_image.copy())
        redo_stack.clear()
        update_canvas(current_image)

def update_canvas(image_to_display):
    global canvas_image, current_image
    current_image = image_to_display
    canvas.delete("all")
    canvas_image = ImageTk.PhotoImage(image_to_display)
    canvas.config(width=image_to_display.width, height=image_to_display.height)
    canvas.create_image(0, 0, image=canvas_image, anchor="nw")

def draw(event):
    if drawing_enabled:
        x1, y1 = (event.x - pen_size), (event.y - pen_size)
        x2, y2 = (event.x + pen_size), (event.y + pen_size)
        draw_on_image(x1, y1, x2, y2)
        update_canvas(current_image)

def draw_on_image(x1, y1, x2, y2):
    global current_image
    image_draw = ImageDraw.Draw(current_image)
    image_draw.ellipse([x1, y1, x2, y2], fill=pen_color, outline=pen_color)
    save_state()

def save_state():
    global current_image, undo_stack, redo_stack
    undo_stack.append(current_image.copy())
    redo_stack.clear()

def undo():
    global current_image
    if len(undo_stack) > 1:
        redo_stack.append(undo_stack.pop())
        current_image = undo_stack[-1]
        update_canvas(current_image)
    elif len(undo_stack) == 1:
        redo_stack.append(undo_stack.pop())
        current_image = original_image.copy()
        update_canvas(current_image)

def redo():
    global current_image
    if redo_stack:
        undo_stack.append(redo_stack.pop())
        current_image = undo_stack[-1]
        update_canvas(current_image)

def clear_canvas():
    global current_image, original_image
    canvas.delete("all")
    if original_image:
        update_canvas(original_image.copy())
        current_image = original_image.copy()
    else:
        canvas.config(width=750, height=600)
    undo_stack.clear()
    redo_stack.clear()

def change_color():
    global pen_color
    pen_color = colorchooser.askcolor(title="Select pen color")[1]

def change_size(size):
    global pen_size
    pen_size = size

def apply_filter(filter):
    global current_image, original_image
    undo_stack.append(current_image.copy())
    redo_stack.clear()
    filtered_image = original_image.copy()
    if filter == "Black and White":
        filtered_image = ImageOps.grayscale(filtered_image)
    elif filter == "Blur":
        filtered_image = filtered_image.filter(ImageFilter.BLUR)
    elif filter == "Sharpen":
        filtered_image = filtered_image.filter(ImageFilter.SHARPEN)
    elif filter == "Smooth":
        filtered_image = filtered_image.filter(ImageFilter.SMOOTH)
    elif filter == "Emboss":
        filtered_image = filtered_image.filter(ImageFilter.EMBOSS)
    update_canvas(filtered_image)

def rotate_image(degrees):
    global current_image, angle
    angle = (angle + degrees) % 360
    rotated_image = current_image.rotate(angle, expand=True)
    undo_stack.append(current_image.copy())
    redo_stack.clear()
    update_canvas(rotated_image)

def enable_crop_mode():
    global is_cropping, drawing_enabled
    is_cropping = True
    drawing_enabled = False
    canvas.config(cursor="cross")

def start_crop(event):
    global start_x, start_y
    if is_cropping:
        start_x, start_y = event.x, event.y
        canvas.delete("crop_rectangle")
        canvas.create_rectangle(start_x, start_y, start_x, start_y, outline="red", tag="crop_rectangle")

def end_crop(event):
    global end_x, end_y, is_cropping, drawing_enabled
    if is_cropping:
        end_x, end_y = event.x, event.y
        canvas.coords("crop_rectangle", start_x, start_y, end_x, end_y)
        is_cropping = False
        drawing_enabled = True
        canvas.config(cursor="")
        crop_image()

def crop_image():
    global current_image, start_x, start_y, end_x, end_y
    if start_x and start_y and end_x and end_y:
        undo_stack.append(current_image.copy())
        redo_stack.clear()
        cropped_image = current_image.crop((start_x, start_y, end_x, end_y))
        update_canvas(cropped_image)
        start_x = start_y = end_x = end_y = None

def revert_to_original():
    global current_image
    if original_image:
        current_image = original_image.copy()
        undo_stack.clear()
        redo_stack.clear()
        update_canvas(current_image)
    else:
        messagebox.showerror("Error", "No original image loaded.")

left_frame = tk.Frame(root, width=200, height=600, bg="white")
left_frame.pack(side="left", fill="y")

canvas = tk.Canvas(root, width=750, height=600)
canvas.pack()

img_button = tk.Button(left_frame, text="Add Image", bg="white", command=add_image)
img_button.pack(pady=15)

color_btn = tk.Button(left_frame, text="Change Pen Color", command=change_color, bg="white")
color_btn.pack(pady=15)

pen_size_frame = tk.Frame(left_frame, bg="white")
pen_size_frame.pack(pady=5)

pen_size_1 = tk.Radiobutton(pen_size_frame, text="Small", value=3, command=lambda: change_size(3), bg="white")
pen_size_1.pack(side="left")
pen_size_2 = tk.Radiobutton(pen_size_frame, text="Medium", value=5, command=lambda: change_size(5), bg="white")
pen_size_2.pack(side="left")
pen_size_2.select()
pen_size_3 = tk.Radiobutton(pen_size_frame, text="Large", value=7, command=lambda: change_size(7), bg="white")
pen_size_3.pack(side="left")

undo_button = tk.Button(left_frame, text="Undo", bg="white", command=undo)
undo_button.pack(pady=15)

redo_button = tk.Button(left_frame, text="Redo", bg="white", command=redo)
redo_button.pack(pady=15)

clear_button = tk.Button(left_frame, text="Clear", bg="white", command=clear_canvas)
clear_button.pack(pady=15)

filter_frame = tk.Frame(left_frame, bg="white")
filter_frame.pack(pady=5)

filter_label = tk.Label(filter_frame, text="Filters", bg="white")
filter_label.pack(pady=5)

filter_options = ["Black and White", "Blur", "Sharpen", "Smooth", "Emboss"]
filter_var = tk.StringVar()
filter_var.set("Select a filter")
filter_menu = ttk.Combobox(filter_frame, textvariable=filter_var, values=filter_options)
filter_menu.pack(pady=5)
filter_menu.bind("<<ComboboxSelected>>", lambda e: apply_filter(filter_var.get()))

rotate_button = tk.Button(left_frame, text="Rotate", bg="white", command=lambda: rotate_image(90))
rotate_button.pack(pady=15)

crop_button = tk.Button(left_frame, text="Crop", bg="white", command=enable_crop_mode)
crop_button.pack(pady=15)

revert_button = tk.Button(left_frame, text="Revert to Original", bg="white", command=revert_to_original)
revert_button.pack(pady=15)

canvas.bind("<B1-Motion>", draw)
canvas.bind("<ButtonPress-1>", start_crop)
canvas.bind("<ButtonRelease-1>", end_crop)

root.mainloop()
