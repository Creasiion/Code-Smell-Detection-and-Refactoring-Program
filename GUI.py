import os
from tkinter import *
from tkinter import filedialog, Toplevel, Frame, Label, Button, messagebox
from tkinter.scrolledtext import ScrolledText
from LongFunctionDetection import detect_long_functions
from LongParameterDetection import detect_long_parameters
from DuplicateFunctionDetection import detect_duplicate_functions, refactor_duplicate_functions

HEADER_SIZE = 25
LABEL_SIZE = 20
NOTIFICATION_SIZE = 15
PAD_X = 10
PAD_Y = 20

def create_code_smell_window():
    resultWindow = Toplevel(window)
    resultWindow.title("Detected Code Smells")
    resultWindow.geometry('500x500')
    
    buttonContainer = Frame(resultWindow)
    buttonContainer.pack(side="bottom", fill="x", pady=PAD_Y)
    
    scrollTextInfo = ScrolledText(resultWindow, wrap=WORD, font=("Arial", LABEL_SIZE))
    scrollTextInfo.pack(side="bottom", expand=True, fill="both")
    scrollTextInfo.tag_configure("header",font=("Arial", HEADER_SIZE, "underline"),justify="center",spacing3=10)
    scrollTextInfo.tag_configure("function",font=("Arial", LABEL_SIZE), justify="center")
    
    return scrollTextInfo, buttonContainer

def display_specific_code_smell(textWidget, smellType, data):
    textWidget.insert(END, f"{smellType}:\n", "header")
    
    if not data:
        textWidget.insert(END, "None\n", "function")
        return
    
    for func in data.keys():
        textWidget.insert(END, f"{func}\n", "function")

def refactor_file(inputFile, duplicates, statusLabel):
    statusLabel.config(text="Refactoring in progress...")
    with open(inputFile, "r") as f:
        sourceCode = f.read()
    
    for (keepFunc, removeFunc) in duplicates.keys():
        sourceCode = refactor_duplicate_functions(sourceCode, keepFunc, removeFunc)
        
    directory, filename = os.path.split(inputFile)
    newFilename = f"refactored_{filename}"
    newPath = os.path.join(directory, newFilename)
        
    with open(newPath, "w") as f:
            f.write(sourceCode)
    statusLabel.config(text="Code has been refactored! See refactored file:\n" + newPath)

def display_all_code_smells(inputFile):
    with open(inputFile, "r") as f:
        sourceCode = f.read()
    
    longParameters = detect_long_parameters(sourceCode)
    longFunctions = detect_long_functions(sourceCode)
    duplicateFunctions = detect_duplicate_functions(sourceCode)
    
    details, refactorButton = create_code_smell_window()

    details.insert(END, f"Selected file:\n{inputFile}\n\n","label")
    display_specific_code_smell(details, "Long Parameters", longParameters)
    display_specific_code_smell(details, "Long Functions", longFunctions)
    display_specific_code_smell(details, "Duplicate Functions", duplicateFunctions)
    if duplicateFunctions:
        status = Label(refactorButton, text="", fg="green",font=("Arial", NOTIFICATION_SIZE))
        Button(refactorButton, text="Refactor Duplicate Code?", fg="red", command=lambda: refactor_file(inputFile, duplicateFunctions, status)).pack(pady=PAD_Y)     
        status.pack(pady=PAD_Y)
        
    details.configure(state="disabled")
        
def import_file():
    userInputFile = filedialog.askopenfilename(
        title="Select a file",
        filetypes=[("Python files", "*.py"), ("All files", "*.*")]
    )
    if userInputFile:
        fileLabel.config(text=f"Selected file:\n{userInputFile}")
        display_all_code_smells(userInputFile)
    else:
        fileLabel.config(text="No file selected")
        
def main():
    global userInputFile, fileLabel, window
    
    window = Tk()

    window.title("Imani's Code Smell Detection and Refactoring Tool")
    window.geometry('500x500')

    Label(window, text="Upload code file below:", font=("Arial", HEADER_SIZE)).pack(pady=PAD_Y)

    fileLabel = Label(window, text="No file selected", fg="blue", font=("Arial", NOTIFICATION_SIZE),wraplength=400, justify=CENTER)
    fileLabel.pack(pady=PAD_Y)

    Button(window, text="Select File", fg="red", command=import_file).pack(pady=PAD_Y)

    window.mainloop()
    
if __name__ == "__main__":
    main()