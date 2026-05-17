import tkinter as tk
from tkinter import filedialog, messagebox
from PyPDF2 import PdfWriter, PdfReader

# מילון תרגומים מרכזי לאפליקציה
LOCALIZATION = {
    "English": {
        "title": "PDF Swiss Army Knife - Split & Merge",
        "splitter_title": "PDF Splitter",
        "choose_split": "Choose PDF to Split",
        "no_file": "No file selected",
        "selected": "Selected:",
        "insert_pages": "Insert pages to split\n(e.g., 1-5, 6-10):",
        "split_btn": "Split PDF",
        "clear_split": "Clear Split File",
        "merger_title": "PDF Merger",
        "add_files": "Add PDF Files",
        "move_up": "Move Up",
        "move_down": "Move Down",
        "delete_file": "Delete File",
        "clear_sel": "Clear Selection",
        "merge_btn": "Merge PDFs",
        "err_title": "Error",
        "err_no_split_file": "No file selected for splitting!",
        "err_invalid_range": "Please enter a valid range (e.g., 1-5)!",
        "err_out_of_bounds": "Range out of bounds. File has {total} pages.",
        "err_fail_split": "Failed to split at range '{page_range}':\n{error}",
        "success_title": "Success",
        "success_split": "PDF files split successfully!",
        "err_no_merge_files": "No files selected!",
        "success_merge": "PDF files merged successfully!",
        "err_general": "An error occurred: {error}"
    },
    "עברית": {
        "title": "אולר שוויצרי ל-PDF - פיצול ומיזוג",
        "splitter_title": "פיצול PDF",
        "choose_split": "בחר קובץ לפיצול",
        "no_file": "לא נבחר קובץ",
        "selected": "נבחר:",
        "insert_pages": "הכנס טווחי עמודים לפיצול\n(דוגמה: 1-5, 6-10):",
        "split_btn": "פצל PDF",
        "clear_split": "נקה קובץ שנבחר",
        "merger_title": "מיזוג PDF",
        "add_files": "הוסף קבצי PDF",
        "move_up": "הזז למעלה",
        "move_down": "הזז למטה",
        "delete_file": "מחק קובץ",
        "clear_sel": "נקה בחירה",
        "merge_btn": "מזג קבצים",
        "err_title": "שגיאה",
        "err_no_split_file": "לא נבחר קובץ לפיצול!",
        "err_invalid_range": "בבקשה הכנס טווח עמודים תקין (למשל 1-5)!",
        "err_out_of_bounds": "הטווח מחוץ לגבולות הקובץ. בקובץ יש {total} עמודים.",
        "err_fail_split": "הפיצול נכשל בטווח '{page_range}':\n{error}",
        "success_title": "הצלחה",
        "success_split": "הקובץ פוצל בהצלחה!",
        "err_no_merge_files": "לא נבחרו קבצים למיזוג!",
        "success_merge": "הקבצים מוזגו בהצלחה!",
        "err_general": "התרחשה שגיאה: {error}"
    }
}


class PDFSplitterFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bd=2, relief=tk.GROOVE)
        self.split_file = None
        self.lang = "עברית"

        # אלמנטים גרפיים
        self.label = tk.Label(self, font=("Arial", 14, "bold"), fg="blue")
        self.label.pack(pady=10)

        self.choose_button = tk.Button(self, command=self.choose_split_file)
        self.choose_button.pack(pady=5)

        self.file_label = tk.Label(self, fg="gray", wraplength=250)
        self.file_label.pack(pady=5)

        self.range_label = tk.Label(self)
        self.range_label.pack(pady=5)

        self.range_entry = tk.Entry(self, width=25)
        self.range_entry.pack(pady=5)

        self.split_button = tk.Button(self, command=self.split_pdf, bg="blue", fg="white")
        self.split_button.pack(pady=5)

        self.clear_split_button = tk.Button(self, command=self.clear_split_file)
        self.clear_split_button.pack(pady=5)

        self.update_ui_strings("עברית")

    def update_ui_strings(self, lang):
        self.lang = lang
        strings = LOCALIZATION[lang]

        self.label.config(text=strings["splitter_title"])
        self.choose_button.config(text=strings["choose_split"])
        self.range_label.config(text=strings["insert_pages"])
        self.split_button.config(text=strings["split_btn"])
        self.clear_split_button.config(text=strings["clear_split"])

        if not self.split_file:
            self.file_label.config(text=strings["no_file"])
        else:
            self.file_label.config(text=f"{strings['selected']}\n{self.split_file}")

    def choose_split_file(self):
        self.split_file = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if self.split_file:
            strings = LOCALIZATION[self.lang]
            self.file_label.config(text=f"{strings['selected']}\n{self.split_file}", fg="black")

    def clear_split_file(self):
        self.split_file = None
        strings = LOCALIZATION[self.lang]
        self.file_label.config(text=strings["no_file"], fg="gray")
        self.range_entry.delete(0, tk.END)

    def split_pdf(self):
        strings = LOCALIZATION[self.lang]
        if not self.split_file:
            messagebox.showerror(strings["err_title"], strings["err_no_split_file"])
            return

        raw_ranges = self.range_entry.get().strip()
        if not raw_ranges:
            messagebox.showerror(strings["err_title"], strings["err_invalid_range"])
            return

        page_ranges = raw_ranges.split(',')
        pdf_reader = PdfReader(self.split_file)
        total_pages = len(pdf_reader.pages)

        for i, page_range in enumerate(page_ranges):
            try:
                start, end = map(int, page_range.split('-'))

                if start < 1 or end > total_pages or start > end:
                    raise ValueError(strings["err_out_of_bounds"].format(total=total_pages))

                pdf_writer = PdfWriter()

                for page in range(start - 1, end):
                    pdf_writer.add_page(pdf_reader.pages[page])

                output_file = f"{self.split_file[:-4]}_part_{i + 1}.pdf"

                with open(output_file, 'wb') as out_pdf:
                    pdf_writer.write(out_pdf)

            except Exception as e:
                messagebox.showerror(strings["err_title"],
                                     strings["err_fail_split"].format(page_range=page_range, error=str(e)))
                return

        messagebox.showinfo(strings["success_title"], strings["success_split"])


class PDFMergerFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bd=2, relief=tk.GROOVE)
        self.files = []
        self.lang = "עברית"

        self.label = tk.Label(self, font=("Arial", 14, "bold"), fg="green")
        self.label.pack(pady=10)

        self.add_button = tk.Button(self, command=self.add_files)
        self.add_button.pack(pady=2)

        self.files_listbox = tk.Listbox(self, width=40, height=8)
        self.files_listbox.pack(pady=5)

        self.move_up_button = tk.Button(self, command=self.move_up)
        self.move_up_button.pack(pady=2)

        self.move_down_button = tk.Button(self, command=self.move_down)
        self.move_down_button.pack(pady=2)

        self.delete_button = tk.Button(self, command=self.delete_file)
        self.delete_button.pack(pady=2)

        self.clear_button = tk.Button(self, command=self.clear_files)
        self.clear_button.pack(pady=2)

        self.merge_button = tk.Button(self, command=self.merge_pdfs, bg="green", fg="white")
        self.merge_button.pack(pady=10)

        self.update_ui_strings("עברית")

    def update_ui_strings(self, lang):
        self.lang = lang
        strings = LOCALIZATION[lang]

        self.label.config(text=strings["merger_title"])
        self.add_button.config(text=strings["add_files"])
        self.move_up_button.config(text=strings["move_up"])
        self.move_down_button.config(text=strings["move_down"])
        self.delete_button.config(text=strings["delete_file"])
        self.clear_button.config(text=strings["clear_sel"])
        self.merge_button.config(text=strings["merge_btn"])

    def add_files(self):
        file_paths = filedialog.askopenfilenames(filetypes=[("PDF files", "*.pdf")])
        for file_path in file_paths:
            if file_path not in self.files:
                self.files.append(file_path)
                self.files_listbox.insert(tk.END, file_path)

    def clear_files(self):
        self.files.clear()
        self.files_listbox.delete(0, tk.END)

    def move_up(self):
        try:
            idx = self.files_listbox.curselection()[0]
            if idx > 0:
                self.files[idx], self.files[idx - 1] = self.files[idx - 1], self.files[idx]
                self.update_listbox()
                self.files_listbox.select_set(idx - 1)
        except IndexError:
            pass

    def move_down(self):
        try:
            idx = self.files_listbox.curselection()[0]
            if idx < len(self.files) - 1:
                self.files[idx], self.files[idx + 1] = self.files[idx + 1], self.files[idx]
                self.update_listbox()
                self.files_listbox.select_set(idx + 1)
        except IndexError:
            pass

    def delete_file(self):
        try:
            idx = self.files_listbox.curselection()[0]
            del self.files[idx]
            self.update_listbox()
        except IndexError:
            strings = LOCALIZATION[self.lang]
            messagebox.showerror(strings["err_title"], strings["delete_file"])

    def update_listbox(self):
        self.files_listbox.delete(0, tk.END)
        for file in self.files:
            self.files_listbox.insert(tk.END, file)

    def merge_pdfs(self):
        strings = LOCALIZATION[self.lang]
        if not self.files:
            messagebox.showerror(strings["err_title"], strings["err_no_merge_files"])
            return

        pdf_writer = PdfWriter()
        try:
            for file in self.files:
                pdf_reader = PdfReader(file)
                pdf_writer.append(pdf_reader)

            output_file = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
            if output_file:
                with open(output_file, 'wb') as out_pdf:
                    pdf_writer.write(out_pdf)
                messagebox.showinfo(strings["success_title"], strings["success_merge"])
        except Exception as e:
            messagebox.showerror(strings["err_title"], strings["err_general"].format(error=str(e)))


class MainApplication:
    def __init__(self, root):
        self.root = root
        self.root.geometry("750x600")  # הגדלנו מעט את הגובה בשביל כפתורי הרדיו

        # פאנל עליון לבחירת שפה
        self.top_frame = tk.Frame(root)
        self.top_frame.pack(side=tk.TOP, fill=tk.X, pady=10)

        # משתנה של Tkinter שיחזיק את השפה שנבחרה
        self.lang_var = tk.StringVar(value="עברית")

        # יצירת כפתורי הרדיו (Radio Buttons)
        self.rb_hebrew = tk.Radiobutton(self.top_frame, text="עברית", variable=self.lang_var, value="עברית",
                                        command=self.on_language_change, font=("Arial", 11, "bold"))
        self.rb_hebrew.pack(side=tk.TOP, anchor=tk.CENTER)

        self.rb_english = tk.Radiobutton(self.top_frame, text="English", variable=self.lang_var, value="English",
                                         command=self.on_language_change, font=("Arial", 11, "bold"))
        self.rb_english.pack(side=tk.TOP, anchor=tk.CENTER)

        # פאנל מרכזי שיכיל את המיזוג והפיצול
        self.content_frame = tk.Frame(root)
        self.content_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # יצירת ה-Frames של הכלים
        self.splitter_frame = PDFSplitterFrame(self.content_frame)
        self.merger_frame = PDFMergerFrame(self.content_frame)

        # הפעלה ראשונית של השפה (עברית כברירת מחדל)
        self.on_language_change()

    def on_language_change(self):
        lang = self.lang_var.get()

        # עדכון כותרת החלון הראשי
        self.root.title(LOCALIZATION[lang]["title"])

        # עדכון מחרוזות הטקסט בתוך ה-Frames
        self.splitter_frame.update_ui_strings(lang)
        self.merger_frame.update_ui_strings(lang)

        # הסרה של ה-Frames לצורך סידור מחדש (RTL או LTR)
        self.splitter_frame.pack_forget()
        self.merger_frame.pack_forget()

        if lang == "עברית":
            # בעברית: מיזוג משמאל (שמאל לימין בקריאה של הכלים), פיצול מימין
            self.merger_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=10)
            self.splitter_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=20, pady=10)
        else:
            # באנגלית: פיצול משמאל, מיזוג מימין
            self.splitter_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=10)
            self.merger_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=20, pady=10)


if __name__ == "__main__":
    root = tk.Tk()
    app = MainApplication(root)
    root.mainloop()