import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import PhotoImage
import processing

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'log'}

# Ensure the uploads directory exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def upload_file():
    file_path = filedialog.askopenfilename(filetypes=[("Text and Log files", "*.txt *.log")])
    if not file_path:
        messagebox.showwarning("No file selected", "Please select a file to upload.")
        return
    
    filename = os.path.basename(file_path)
    if allowed_file(filename):
        upload_path = os.path.join(UPLOAD_FOLDER, filename)
        shutil.copy(file_path, upload_path)
        
        # Process the file and generate the excel file
        output_file = processing.process_logs(upload_path)
        
        # Ask the user where to save the output file
        save_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        if save_path:
            shutil.move(os.path.join(UPLOAD_FOLDER, output_file), save_path)
            messagebox.showinfo("Success", f"File processed and saved as {save_path}")
        
        # Clear the uploads cache
        shutil.rmtree(UPLOAD_FOLDER)
        os.makedirs(UPLOAD_FOLDER)
    else:
        messagebox.showwarning("Invalid file", "Only .txt and .log files are allowed.")

# Setup Tkinter window
root = tk.Tk()
root.title("Winfiol Voice Routing Log to Excel Converter")
root.geometry("700x400")

# Set the icon
icon_path = os.path.join("assets", "world.ico")
root.iconbitmap(icon_path)

title_label = tk.Label(root, text="Diego Yaldo", font=("Segoe UI", 24))
title_label.pack(pady=10)

subtitle_label = tk.Label(root, text="Winfiol Voice Routing Log to Excel Converter", font=("Segoe UI", 16))
subtitle_label.pack(pady=5)

upload_btn = tk.Button(root, text="Upload File", command=upload_file, bg="gray", fg="white", font=("Segoe UI", 14))
upload_btn.pack(pady=20)

footer_label = tk.Label(root, text="This code is actively being developed and is in the testing phase.\nPlease note that it may still undergo changes, bug fixes, and optimizations.\nThere may be discrepancies between the routing log and excel sheet, please apply this tool with caution.", font=("Segoe UI", 10), fg="#6c757d", justify=tk.CENTER)
footer_label.pack(pady=10)

root.mainloop()
