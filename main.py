import tkinter as tk
from tkinter import filedialog, messagebox
from PyPDF2 import PdfWriter, PdfReader


class PDFSplitterFrame(tk.Frame):
    def __init__(self, master):
        # תיקון השגיאה: שימוש ב-padx ו-pady מתוך פונקציית ה-pack במקום padding ב-init
        super().__init__(master, bd=2, relief=tk.GROOVE)
        self.split_file = None

        # PDF Splitter Section Title
        self.label = tk.Label(self, text="PDF Splitter", font=("Arial", 14, "bold"), fg="blue")
        self.label.pack(pady=10)

        self.choose_button = tk.Button(self, text="Choose PDF to Split", command=self.choose_split_file)
        self.choose_button.pack(pady=5)

        self.file_label = tk.Label(self, text="No file selected", fg="gray", wraplength=250)
        self.file_label.pack(pady=5)

        self.range_label = tk.Label(self, text="Insert pages to split\n(e.g., 1-5, 6-10):")
        self.range_label.pack(pady=5)

        self.range_entry = tk.Entry(self, width=25)
        self.range_entry.pack(pady=5)

        self.split_button = tk.Button(self, text="Split PDF", command=self.split_pdf, bg="blue", fg="white")
        self.split_button.pack(pady=5)

        self.clear_split_button = tk.Button(self, text="Clear Split File", command=self.clear_split_file)
        self.clear_split_button.pack(pady=5)

    def choose_split_file(self):
        self.split_file = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if self.split_file:
            self.file_label.config(text=f"Selected:\n{self.split_file}", fg="black")

    def clear_split_file(self):
        self.split_file = None
        self.file_label.config(text="No file selected", fg="gray")
        self.range_entry.delete(0, tk.END)

    def split_pdf(self):
        if not self.split_file:
            messagebox.showerror("Error", "No file selected for splitting!")
            return

        raw_ranges = self.range_entry.get().strip()
        if not raw_ranges:
            messagebox.showerror("Error", "Please enter a valid range (e.g., 1-5)!")
            return

        page_ranges = raw_ranges.split(',')
        pdf_reader = PdfReader(self.split_file)
        total_pages = len(pdf_reader.pages)

        for i, page_range in enumerate(page_ranges):
            try:
                start, end = map(int, page_range.split('-'))

                # Validation to avoid index crash
                if start < 1 or end > total_pages or start > end:
                    raise ValueError(f"Range out of bounds. File has {total_pages} pages.")

                pdf_writer = PdfWriter()

                # Adding specified page range to the new PDF (0-indexed)
                for page in range(start - 1, end):
                    pdf_writer.add_page(pdf_reader.pages[page])

                output_file = f"{self.split_file[:-4]}_part_{i + 1}.pdf"

                with open(output_file, 'wb') as out_pdf:
                    pdf_writer.write(out_pdf)

            except Exception as e:
                messagebox.showerror("Error", f"Failed to split at range '{page_range}':\n{str(e)}")
                return

        messagebox.showinfo("Success", "PDF files split successfully!")


class PDFMergerFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bd=2, relief=tk.GROOVE)
        self.files = []

        # PDF Merger Section Title
        self.label = tk.Label(self, text="PDF Merger", font=("Arial", 14, "bold"), fg="green")
        self.label.pack(pady=10)

        self.add_button = tk.Button(self, text="Add PDF Files", command=self.add_files)
        self.add_button.pack(pady=2)

        self.files_listbox = tk.Listbox(self, width=40, height=8)
        self.files_listbox.pack(pady=5)

        self.move_up_button = tk.Button(self, text="Move Up", command=self.move_up)
        self.move_up_button.pack(pady=2)

        self.move_down_button = tk.Button(self, text="Move Down", command=self.move_down)
        self.move_down_button.pack(pady=2)

        self.delete_button = tk.Button(self, text="Delete File", command=self.delete_file)
        self.delete_button.pack(pady=2)

        self.clear_button = tk.Button(self, text="Clear Selection", command=self.clear_files)
        self.clear_button.pack(pady=2)

        self.merge_button = tk.Button(self, text="Merge PDFs", command=self.merge_pdfs, bg="green", fg="white")
        self.merge_button.pack(pady=10)

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
            messagebox.showerror("Error", "No file selected!")

    def update_listbox(self):
        self.files_listbox.delete(0, tk.END)
        for file in self.files:
            self.files_listbox.insert(tk.END, file)

    def merge_pdfs(self):
        if not self.files:
            messagebox.showerror("Error", "No files selected!")
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
                messagebox.showinfo("Success", "PDF files merged successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    root.title("PDF Swiss Army Knife - Split & Merge")
    root.geometry("750x550")

    # יצירת הצד השמאלי - פיצול (הוספתי את הפדינג כאן ב-pack)
    splitter_frame = PDFSplitterFrame(root)
    splitter_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=20)

    # יצירת הצד הימני - מיזוג
    merger_frame = PDFMergerFrame(root)
    merger_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=20, pady=20)

    root.mainloop()