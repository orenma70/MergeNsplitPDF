import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.scrolledtext import ScrolledText  # רכיב ייעודי לחלון פלט עם גלילה
from PyPDF2 import PdfWriter, PdfReader
from PIL import Image
import fitz  # PyMuPDF
import numpy as np

# מילון תרגומים מרכזי לאפליקציה המורחבת
LOCALIZATION = {
    "English": {
        "title": "PDF Swiss Army Knife - Split, Merge & Compare",
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
        "comparer_title": "PDF Visual Compare",
        "old_files_lbl": "Old Files (Base)",
        "new_files_lbl": "New Files (To Compare)",
        "output_dir_lbl": "Select Output Folder for Diff PDFs",
        "choose_dir_btn": "Choose Output Folder",
        "compare_btn": "Run Visual Compare",
        "clear_log_btn": "Clear Log",
        "console_title": "Execution Log / Console Output:",
        "err_title": "Error",
        "err_no_split_file": "No file selected for splitting!",
        "err_invalid_range": "Please enter a valid range (e.g., 1-5)!",
        "err_out_of_bounds": "Range out of bounds. File has {total} pages.",
        "err_fail_split": "Failed to split at range '{page_range}':\n{error}",
        "success_title": "Success",
        "success_split": "PDF files split successfully!",
        "err_no_merge_files": "No files selected!",
        "success_merge": "PDF files merged successfully!",
        "err_general": "An error occurred: {error}",
        "err_compare_mismatch": "Error: The number of Old files ({old_cnt}) does not match New files ({new_cnt})!",
        "err_no_out_dir": "Please select an output folder for the diff results!",
        "err_page_count_mismatch": "Error in pair {idx}: Page counts do not match ({old_p} vs {new_p}) for:\n{name}",
        "compare_complete": "Comparison complete!\nResults saved to output directory."
    },
    "עברית": {
        "title": "אולר שוויצרי ל-PDF - פיצול, מיזוג והשוואה",
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
        "comparer_title": "השוואה חזותית בין קבצים",
        "old_files_lbl": "קבצים ישנים (מקור)",
        "new_files_lbl": "קבצים חדשים (להשוואה)",
        "output_dir_lbl": "בחר תיקיית יעד לקבצי הצימוד (Diff)",
        "choose_dir_btn": "בחר תיקיית פלט",
        "compare_btn": "הפעל השוואה חזותית",
        "clear_log_btn": "נקה לוג",
        "console_title": "חלון פלט / לוג ריצה:",
        "err_title": "שגיאה",
        "err_no_split_file": "לא נבחר קובץ לפיצול!",
        "err_invalid_range": "בבקשה הכנס טווח עמודים תקין (למשל 1-5)!",
        "err_out_of_bounds": "הטווח מחוץ לגבולות הקובץ. בקובץ יש {total} עמודים.",
        "err_fail_split": "הפיצול נכשל בטווח '{page_range}':\n{error}",
        "success_title": "הצלחה",
        "success_split": "הקובץ פוצל בהצלחה!",
        "err_no_merge_files": "לא נבחרו קבצים למיזוג!",
        "success_merge": "הקבצים מוזגו בהצלחה!",
        "err_general": "התרחשה שגיאה: {error}",
        "err_compare_mismatch": "שגיאה: מספר הקבצים הישנים ({old_cnt}) אינו תואם למספר החדשים ({new_cnt})!",
        "err_no_out_dir": "יש לבחור תיקיית פלט לשמירת תוצאות ההשוואה!",
        "err_page_count_mismatch": "שגיאה בצמד {idx}: כמות העמודים אינה תואמת ({old_p} מול {new_p}) עבור:\n{name}",
        "compare_complete": "ההשוואה הסתיימה בהצלחה!\nהתוצאות נשמרו בתיקייה שנבחרה."
    }
}


class PDFSplitterFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bd=2, relief=tk.GROOVE)
        self.split_file = None
        self.lang = "עברית"

        self.label = tk.Label(self, font=("Arial", 12, "bold"), fg="blue")
        self.label.pack(pady=10)

        self.choose_button = tk.Button(self, command=self.choose_split_file)
        self.choose_button.pack(pady=5)

        self.file_label = tk.Label(self, fg="gray", wraplength=200)
        self.file_label.pack(pady=5)

        self.range_label = tk.Label(self)
        self.range_label.pack(pady=5)

        self.range_entry = tk.Entry(self, width=20)
        self.range_entry.pack(pady=5)

        self.split_button = tk.Button(self, command=self.split_pdf, bg="blue", fg="white")
        self.split_button.pack(pady=5)

        self.clear_split_button = tk.Button(self, command=self.clear_split_file)
        self.clear_split_button.pack(pady=5)

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

        self.label = tk.Label(self, font=("Arial", 12, "bold"), fg="green")
        self.label.pack(pady=10)

        self.add_button = tk.Button(self, command=self.add_files)
        self.add_button.pack(pady=2)

        self.files_listbox = tk.Listbox(self, width=35, height=8)
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


class PDFComparerFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bd=2, relief=tk.GROOVE)
        self.old_files = []
        self.new_files = []
        self.output_dir = None
        self.lang = "עברית"

        self.label = tk.Label(self, font=("Arial", 12, "bold"), fg="purple")
        self.label.pack(pady=5)

        # פאנל פנימי לשני טורים של רשימות קבצים
        self.lists_frame = tk.Frame(self)
        self.lists_frame.pack(fill=tk.X, padx=5)

        # טור שמאל - קבצים ישנים
        self.old_frame = tk.Frame(self.lists_frame)
        self.old_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=2)
        self.old_lbl = tk.Label(self.old_frame, font=("Arial", 10, "bold"))
        self.old_lbl.pack()
        self.old_btn = tk.Button(self.old_frame, text="+", command=lambda: self.add_compare_files("old"))
        self.old_btn.pack(pady=2)
        self.old_listbox = tk.Listbox(self.old_frame, width=22, height=5)
        self.old_listbox.pack(fill=tk.BOTH, expand=True)
        self.create_management_buttons(self.old_frame, "old")

        # טור ימין - קבצים חדשים
        self.new_frame = tk.Frame(self.lists_frame)
        self.new_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=2)
        self.new_lbl = tk.Label(self.new_frame, font=("Arial", 10, "bold"))
        self.new_lbl.pack()
        self.new_btn = tk.Button(self.new_frame, text="+", command=lambda: self.add_compare_files("new"))
        self.new_btn.pack(pady=2)
        self.new_listbox = tk.Listbox(self.new_frame, width=22, height=5)
        self.new_listbox.pack(fill=tk.BOTH, expand=True)
        self.create_management_buttons(self.new_frame, "new")

        # בחירת תיקיית פלט לתוצאות
        self.dir_frame = tk.Frame(self)
        self.dir_frame.pack(pady=5, fill=tk.X)
        self.dir_lbl = tk.Label(self.dir_frame, text="", wraplength=220, fg="gray", font=("Arial", 9))
        self.dir_lbl.pack()
        self.dir_btn = tk.Button(self.dir_frame, command=self.choose_output_dir)
        self.dir_btn.pack(pady=2)

        # כפתורי הפעלה וניקוי לוג בשורה אחת
        self.control_frame = tk.Frame(self)
        self.control_frame.pack(pady=5)

        self.compare_button = tk.Button(self.control_frame, command=self.run_visual_compare, bg="purple", fg="white",
                                        font=("Arial", 10, "bold"))
        self.compare_button.pack(side=tk.LEFT, padx=5)

        self.clear_log_button = tk.Button(self.control_frame, command=self.clear_log, font=("Arial", 10))
        self.clear_log_button.pack(side=tk.LEFT, padx=5)

        # חלון פלט דמוי קונסול (Console Output Window)
        self.console_label = tk.Label(self, font=("Arial", 9, "bold"))
        self.console_label.pack(anchor=tk.W if self.lang == "English" else tk.E, padx=5, pady=(5, 0))

        # תיבת טקסט לבנה עם גלילה (ScrolledText)
        self.console_text = ScrolledText(self, height=8, width=40, bg="white", fg="black", font=("Consolas", 9))
        self.console_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        # הפיכת החלון ל-Disabled כברירת מחדל כדי שהמשתמש לא יקליד בפנים בטעות
        self.console_text.config(state=tk.DISABLED)

    def create_management_buttons(self, parent_frame, list_type):
        btn_frame = tk.Frame(parent_frame)
        btn_frame.pack(pady=2)
        tk.Button(btn_frame, text="▲", command=lambda: self.move_item(list_type, -1)).pack(side=tk.LEFT, padx=1)
        tk.Button(btn_frame, text="▼", command=lambda: self.move_item(list_type, 1)).pack(side=tk.LEFT, padx=1)
        tk.Button(btn_frame, text="X", command=lambda: self.delete_item(list_type)).pack(side=tk.LEFT, padx=1)
        tk.Button(btn_frame, text="CLR", command=lambda: self.clear_list(list_type)).pack(side=tk.LEFT, padx=1)

    def update_ui_strings(self, lang):
        self.lang = lang
        strings = LOCALIZATION[lang]
        self.label.config(text=strings["comparer_title"])
        self.old_lbl.config(text=strings["old_files_lbl"])
        self.new_lbl.config(text=strings["new_files_lbl"])
        self.dir_btn.config(text=strings["choose_dir_btn"])
        self.compare_button.config(text=strings["compare_btn"])
        self.clear_log_button.config(text=strings["clear_log_btn"])
        self.console_label.config(text=strings["console_title"])

        # עדכון כיוון יישור הכותרת של הקונסול
        self.console_label.pack_configure(anchor=tk.W if lang == "English" else tk.E)

        if not self.output_dir:
            self.dir_lbl.config(text=strings["output_dir_lbl"])
        else:
            self.dir_lbl.config(text=f"{strings['selected']} {self.output_dir}")

    def log_to_console(self, text_message):
        """פונקציית עזר להזרקת שורות לחלון הפלט בזמן אמת"""
        self.console_text.config(state=tk.NORMAL)  # פתיחה לכתיבה
        self.console_text.insert(tk.END, text_message + "\n")
        self.console_text.see(tk.END)  # גלילה אוטומטית לסוף הטקסט
        self.console_text.config(state=tk.DISABLED)  # נעילה מחדש
        self.update_idletasks()  # מאלץ את ה-GUI לרענן את המסך מיד!

    def clear_log(self):
        self.console_text.config(state=tk.NORMAL)
        self.console_text.delete(1.0, tk.END)
        self.console_text.config(state=tk.DISABLED)

    def add_compare_files(self, list_type):
        file_paths = filedialog.askopenfilenames(filetypes=[("PDF files", "*.pdf")])
        target_list = self.old_files if list_type == "old" else self.new_files
        target_listbox = self.old_listbox if list_type == "old" else self.new_listbox

        for path in file_paths:
            if path not in target_list:
                target_list.append(path)
                target_listbox.insert(tk.END, path.split('/')[-1])

    def clear_list(self, list_type):
        if list_type == "old":
            self.old_files.clear()
            self.old_listbox.delete(0, tk.END)
        else:
            self.new_files.clear()
            self.new_listbox.delete(0, tk.END)

    def delete_item(self, list_type):
        lb = self.old_listbox if list_type == "old" else self.new_listbox
        target_list = self.old_files if list_type == "old" else self.new_files
        try:
            idx = lb.curselection()[0]
            del target_list[idx]
            lb.delete(idx)
        except IndexError:
            pass

    def move_item(self, list_type, direction):
        lb = self.old_listbox if list_type == "old" else self.new_listbox
        target_list = self.old_files if list_type == "old" else self.new_files
        try:
            idx = lb.curselection()[0]
            new_idx = idx + direction
            if 0 <= new_idx < len(target_list):
                target_list[idx], target_list[new_idx] = target_list[new_idx], target_list[idx]
                lb.delete(0, tk.END)
                for path in target_list:
                    lb.insert(tk.END, path.split('/')[-1])
                lb.select_set(new_idx)
        except IndexError:
            pass

    def choose_output_dir(self):
        self.output_dir = filedialog.askdirectory()
        if self.output_dir:
            strings = LOCALIZATION[self.lang]
            self.dir_lbl.config(text=f"{strings['selected']} {self.output_dir}", fg="black")

    def read_page_as_1bit_array(self, pdf_path, page_num):
        doc = fitz.open(pdf_path)
        pix = doc[page_num].get_pixmap(dpi=300)
        img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        img_1bit = img.convert('1')
        doc.close()
        return np.array(img_1bit)

    def run_visual_compare(self):
        strings = LOCALIZATION[self.lang]
        if len(self.old_files) != len(self.new_files):
            messagebox.showerror(strings["err_title"],
                                 strings["err_compare_mismatch"].format(old_cnt=len(self.old_files),
                                                                        new_cnt=len(self.new_files)))
            return
        if not self.output_dir:
            messagebox.showerror(strings["err_title"], strings["err_no_out_dir"])
            return

        self.log_to_console("++++++++++++++++++++++++++++++")
        self.log_to_console("Starting Visual PDF Compare...")

        for inx in range(len(self.old_files)):
            old_path = self.old_files[inx]
            new_path = self.new_files[inx]
            file_name = old_path.split('/')[-1][:-4]

            self.log_to_console(f"Processing: {old_path.split('/')[-1]}")

            olddoc = fitz.open(old_path)
            newdoc = fitz.open(new_path)
            Np_old = olddoc.page_count
            Np_new = newdoc.page_count
            olddoc.close()
            newdoc.close()

            if Np_new != Np_old:
                err_msg = strings["err_page_count_mismatch"].format(idx=inx + 1, old_p=Np_old, new_p=Np_new,
                                                                    name=file_name)
                self.log_to_console(f"ERROR: {err_msg}")
                messagebox.showerror(strings["err_title"], err_msg)
                return

            diffarray1 = []
            diffarray3 = []
            difflag = False

            for page_num in range(Np_new):
                image_old = self.read_page_as_1bit_array(old_path, page_num)
                image_new = self.read_page_as_1bit_array(new_path, page_num)

                diff = image_old ^ image_new
                num_differing_pixels = np.sum(diff)

                if num_differing_pixels > 0:
                    difflag = True
                    self.log_to_console(
                        f"  -> Page num {page_num + 1} num_differing_pixels={num_differing_pixels} is NOT OK!!!")
                    diff = np.logical_not(diff)
                    concatenated_images = np.concatenate([image_old, image_new, diff], axis=1)

                    diff_image3 = Image.fromarray(concatenated_images)
                    diff_image1 = Image.fromarray(diff)

                    diffarray3.append(diff_image3)
                    diffarray1.append(diff_image1)
                else:
                    self.log_to_console(f"  -> Page num {page_num + 1} is OK.")

            if difflag:
                diff_path1 = f"{self.output_dir}/diff_{file_name}_mode1.pdf"
                diff_path3 = f"{self.output_dir}/diff_{file_name}_mode3.pdf"
                diffarray1[0].save(diff_path1, save_all=True, append_images=diffarray1[1:])
                diffarray3[0].save(diff_path3, save_all=True, append_images=diffarray3[1:])
                self.log_to_console(f"Diff saved for {file_name}")

        self.log_to_console("Compare finished completely.")
        messagebox.showinfo(strings["success_title"], strings["compare_complete"])


class MainApplication:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1150x700")  # הגדלנו את הגובה מעט בשביל תיבת הקונסול

        self.top_frame = tk.Frame(root)
        self.top_frame.pack(side=tk.TOP, fill=tk.X, pady=10)

        self.lang_var = tk.StringVar(value="עברית")

        self.rb_hebrew = tk.Radiobutton(self.top_frame, text="עברית", variable=self.lang_var, value="עברית",
                                        command=self.on_language_change, font=("Arial", 11, "bold"))
        self.rb_hebrew.pack(side=tk.TOP, anchor=tk.CENTER)

        self.rb_english = tk.Radiobutton(self.top_frame, text="English", variable=self.lang_var, value="English",
                                         command=self.on_language_change, font=("Arial", 11, "bold"))
        self.rb_english.pack(side=tk.TOP, anchor=tk.CENTER)

        self.content_frame = tk.Frame(root)
        self.content_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.splitter_frame = PDFSplitterFrame(self.content_frame)
        self.merger_frame = PDFMergerFrame(self.content_frame)
        self.comparer_frame = PDFComparerFrame(self.content_frame)

        self.on_language_change()

    def on_language_change(self):
        lang = self.lang_var.get()
        self.root.title(LOCALIZATION[lang]["title"])

        self.splitter_frame.update_ui_strings(lang)
        self.merger_frame.update_ui_strings(lang)
        self.comparer_frame.update_ui_strings(lang)

        self.splitter_frame.pack_forget()
        self.merger_frame.pack_forget()
        self.comparer_frame.pack_forget()

        if lang == "עברית":
            self.comparer_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
            self.splitter_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
            self.merger_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        else:
            self.splitter_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
            self.merger_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
            self.comparer_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)


if __name__ == "__main__":
    root = tk.Tk()
    app = MainApplication(root)
    root.mainloop()