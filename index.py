import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os

# Global variables to store the resized width and height of the image from Frame 1
frame1_resized_width = None
frame1_resized_height = None

# Function to encode a message into an image using LSB steganography
def encode_lsb(image_path, message, lsb_plane):
    img = Image.open(image_path)
    width, height = img.size

    # Append a null terminator to the message
    message += '\x00'

    binary_message = ''.join(format(ord(char), '08b') for char in message)  # Convert message to binary

    if len(binary_message) > width * height * 3:  # Check if message is too large for the image
        raise ValueError("Message is too large for the image")

    index = 0
    for y in range(height):
        for x in range(width):
            pixel = list(img.getpixel((x, y)))
            for i in range(3):  # Iterate over RGB channels
                if index < len(binary_message):
                    # Encode the bits of the message into the specified LSB plane of each RGB channel
                    pixel[i] &= ~(1 << lsb_plane)  # Clear the specified bit of the channel
                    pixel[i] |= int(binary_message[index]) << lsb_plane
                    index += 1
            img.putpixel((x, y), tuple(pixel))

    return img

def decode_lsb(image_path, lsb_plane):
    img = Image.open(image_path)
    width, height = img.size
    binary_message = ""

    found_null = False
    for y in range(height):
        for x in range(width):
            pixel = img.getpixel((x, y))
            for i in range(3):  # Iterate over RGB channels
                # Extract the specified LSB plane bit of each RGB channel
                bit = (pixel[i] >> lsb_plane) & 1
                binary_message += str(bit)
            if binary_message[-8:] == '00000000':
                found_null = True
                break
        if found_null:
            break

    # Convert binary message to ASCII
    message = ""
    for i in range(0, len(binary_message), 8):
        byte = binary_message[i:i+8]
        char = chr(int(byte, 2))
        if char == '\x00':  # Stop when encountering null character
            break
        message += char

    return message.strip()

def show_image():
    global filename, frame1_resized_width, frame1_resized_height
    filename = filedialog.askopenfilename(initialdir=os.getcwd(),
                                          title='Select Image File',
                                          filetypes=(("PNG file", "*.png"),
                                                     ("JPG File", "*.jpg"),
                                                     ("All files", "*.*")))
    if filename:
        img = Image.open(filename)
        width, height = img.size

        # Set fixed width and height for Frame 1
        frame1_width = 600
        frame1_height = 400

        # Calculate the ratio to fit the image within the frame while maintaining aspect ratio
        width_ratio = frame1_width / width
        height_ratio = frame1_height / height
        resize_ratio = min(width_ratio, height_ratio)

        frame1_resized_width = int(width * resize_ratio)
        frame1_resized_height = int(height * resize_ratio)

        img = img.resize((frame1_resized_width, frame1_resized_height), Image.LANCZOS)
        img = ImageTk.PhotoImage(img)

        lbl.configure(image=img)  # Configure the image in lbl (Frame 1)
        lbl.image = img  # Keep a reference to prevent garbage collection

def hide_message():
    global secret, new_image_label
    message = text1.get(1.0, tk.END)
    if filename and message:
        try:
            lsb_plane = lsb_var.get()
            secret = encode_lsb(filename, message, lsb_plane)
            messagebox.showinfo("Success", "Message hidden successfully!")

            # Display the new image with the hidden text in Frame 6 without resizing
            new_image = secret.copy()
            new_image = new_image.resize((frame1_resized_width, frame1_resized_height), Image.LANCZOS)  # Resize to match Frame 1
            new_image = ImageTk.PhotoImage(new_image)

            new_image_label.configure(image=new_image)
            new_image_label.image = new_image

            # Prevent Frame 6 from expanding and maintain the image size
            frame6.grid_propagate(False)
            frame6.grid_rowconfigure(0, weight=0)
            frame6.grid_columnconfigure(0, weight=0)

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    else:
        messagebox.showwarning("Warning", "Please select an image and enter a message.")

# Rest of your code remains unchanged...


def show_message():
    global filename
    if filename:
        try:
            lsb_plane = lsb_var.get()  # Get the selected LSB plane from the variable
            clear_message = decode_lsb(filename, lsb_plane)
            text1.delete(1.0, tk.END)
            text1.insert(tk.END, clear_message)
            messagebox.showinfo("Success", "Message revealed successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    else:
        messagebox.showwarning("Warning", "Please select an image first.")

def save_image():
    if filename:
        try:
            save_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                      filetypes=(("PNG files", ".png"), ("All files", ".*")))
            if save_path:
                secret.save(save_path)
                messagebox.showinfo("Success", f"Image saved successfully at {save_path}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    else:
        messagebox.showwarning("Warning", "Please select an image first.")

# GUI setup
root = tk.Tk()
root.title("Steganography - Hide a Secret Text Message in an Image")
root.state('zoomed')  # Open the window maximized
root.configure(bg="#22223b")

# Label 
label = tk.Label(root, text="DRM FOR COPYRIGHT INFORMATION", font=("Arial", 18, "bold"), bg="#22223b", fg="white")
label.grid(row=0, column=0, columnspan=4, padx=10, pady=10)

# First Frame (Frame 1)
f = tk.Frame(root, bd=3, bg="black", relief=tk.GROOVE, width=600, height=400)  # Set fixed width and height
f.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")  # Removed rowspans
lbl = tk.Label(f, bg="black")  # Removed width and height of label
lbl.pack(fill=tk.BOTH, expand=True)

# Sixth Frame 
frame6 = tk.Frame(root, bd=3, bg="black", relief=tk.GROOVE, width=600, height=400)  # Set fixed width and height (same as Frame 1)
frame6.grid(row=1, column=2, columnspan=2, padx=10, pady=10, sticky="nsew")  # Removed rowspan

# Labels for frames
lbl = tk.Label(f, bg="black")  # Removed width and height of label
lbl.pack(fill=tk.BOTH, expand=True)
new_image_label = tk.Label(frame6, bg="black")
new_image_label.pack(fill=tk.BOTH, expand=True)

# Second Frame
frame2 = tk.Frame(root, bd=3, bg="white", relief=tk.GROOVE)
frame2.grid(row=5, column=0, columnspan=4, padx=(10, 20), pady=10, sticky="nsew")  # Added padx=(10, 20)
text1 = tk.Text(frame2, font="Arial 12", bg="white", fg="black", relief=tk.GROOVE, wrap=tk.WORD, height=5)  # Adjusted height
text1.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Third Frame
frame3 = tk.Frame(root, bd=3, bg="#22223b", relief=tk.GROOVE)
frame3.grid(row=6, column=0, padx=10, pady=10, sticky="nsew")
tk.Button(frame3, text="Open Image", width=10, height=2, font="Arial 12 bold", command=show_image).pack(side=tk.LEFT, padx=(0, 5), pady=10, fill=tk.BOTH, expand=True)
tk.Button(frame3, text="Save Image", width=10, height=2, font="Arial 12 bold", command=save_image).pack(side=tk.RIGHT, padx=(5, 0), pady=10, fill=tk.BOTH, expand=True)

# Fourth Frame
frame4 = tk.Frame(root, bd=3, bg="#22223b", relief=tk.GROOVE)
frame4.grid(row=6, column=1, padx=(10, 20), pady=10, sticky="nsew")  # Added padx=(10, 20)
tk.Button(frame4, text="Hide Data", width=10, height=2, font="Arial 12 bold", command=hide_message).pack(side=tk.LEFT, padx=(0, 5), pady=10, fill=tk.BOTH, expand=True)
tk.Button(frame4, text="Show Data", width=10, height=2, font="Arial 12 bold", command=show_message).pack(side=tk.RIGHT, padx=(5, 0), pady=10, fill=tk.BOTH, expand=True)

# Fifth Frame
frame5 = tk.Frame(root, bd=3, bg="#22223b", relief=tk.GROOVE)
frame5.grid(row=6, column=2, padx=(0, 10), pady=10, sticky="nsew", columnspan=2)  # Added padx=(0, 10)
tk.Button(frame5, text="Image Properties", width=30, height=2, font="Arial 12 bold").pack(side=tk.RIGHT, padx=(5, 0), pady=10, fill=tk.BOTH, expand=True)


# LSB Plane Selection
lsb_var = tk.IntVar()
lsb_var.set(0)  # Default to LSB plane 0
lsb_radio_frame = tk.Frame(root, bg="#22223b")
lsb_radio_frame.grid(row=7, column=0, columnspan=4, pady=10)  # Changed columnspan to 3
for i in range(8):
    tk.Radiobutton(lsb_radio_frame, text=f"LSB {i}", variable=lsb_var, value=i, bg="#22223b").pack(side=tk.LEFT, padx=5)


# Configure row and column weights to expand with the window
root.grid_rowconfigure(1, weight=1) # Row 1 weight
root.grid_columnconfigure(0, weight=1)  # Column 0 weight
root.grid_columnconfigure(1, weight=1)  # Column 1 weight
root.grid_columnconfigure(2, weight=1)  # Column 2 weight
root.grid_columnconfigure(3, weight=1)  # Column 3 weight


root.mainloop()
