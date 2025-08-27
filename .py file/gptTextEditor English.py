import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk, messagebox
import re, os

# Try to import python-docx
try:
    from docx import Document
    HAS_DOCX = True
except Exception:
    HAS_DOCX = False

class GPTTextEditApp:
    def __init__(self, root):
        self.root = root
        self.root.title('GPTtextEditor GPT ')
        self.root.geometry('700x900')  # Larger window size

        # Enlarge global default fonts (including messagebox)
        tkfont.nametofont("TkDefaultFont").configure(size=16)
        tkfont.nametofont("TkTextFont").configure(size=14)
        tkfont.nametofont("TkHeadingFont").configure(size=20)

        self.create_widgets()

    def show_help(self):
        msg = (
            "Instructions for this software:\n"
            "1. Add （add colon after each subtitle) at the end of your GPT question\n"
            "2. Check the box 'Already required GPT to add colon after each subtitle!'\n"
            "3. Copy GPT's answer and paste it into the big text box\n"
            "4. Click 'One-click Format', the formatted content will be automatically saved as a document in the root directory!"
        )
        messagebox.showinfo("Help", msg)

    def create_widgets(self):
        container = ttk.Frame(self.root, padding=12)
        container.grid(row=0, column=0, sticky="nsew")

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        container.columnconfigure(0, weight=0)
        container.columnconfigure(1, weight=1)
        container.columnconfigure(2, weight=1)   # Allow the column with "Start button" to expand
        container.columnconfigure(3, weight=0)
        # Row 5 (where text box is) should expand
        container.rowconfigure(5, weight=1)

        # Larger widget styles
        style = ttk.Style(self.root)
        style.configure("Start.TButton", font=("Arial", 14), padding=(28, 12))   # Large button
        style.configure("Big.TCheckbutton", font=("Arial", 13))                  # Large checkbox
        style.configure("Big.TLabel", font=("Arial", 12))                        # Large label

        # Title
        title = ttk.Label(container, text="GPT Text Auto Formatter", font=("Arial", 16))
        title.grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 8))

        # Top label
        lbl = ttk.Label(container, text="Please enter text copied from GPT:", style="Big.TLabel")
        lbl.grid(row=1, column=0, sticky="w", padx=(0, 8))

        # One-click Format (make larger, stretched, shift left and span two columns to avoid overlap)
        start_btn = ttk.Button(container, text="One-click Format",
                               command=self.start_edit, style="Start.TButton")
        start_btn.grid(row=1, column=1, columnspan=2, sticky="ew", padx=(0, 5))

        # Right-side help/clear buttons
        right_btns = ttk.Frame(container)
        right_btns.grid(row=1, column=3, sticky="ne")

        help_btn = ttk.Button(right_btns, text="Help", command=self.show_help)
        help_btn.grid(row=0, column=0, sticky="ew", pady=(0, 4))

        clear_btn = ttk.Button(right_btns, text="Clear", command=self.empty)
        clear_btn.grid(row=1, column=0, sticky="ew")

        # Filename input (optional)
        name_lbl = ttk.Label(container, text="Filename to save (optional):", style="Big.TLabel")
        name_lbl.grid(row=2, column=0, sticky="w", padx=(0, 8), pady=(6, 0))
        self.filename_entry = ttk.Entry(container)
        self.filename_entry.grid(row=2, column=1, columnspan=3, sticky="ew", pady=(6, 0))

        # Checkboxes (each takes one row)
        # Put "Already required colon" in the first row
        self.require_colon = tk.BooleanVar(value=False)
        require_colon_check = ttk.Checkbutton(
            container,
            text="Already required GPT answers to add colon after each subtitle!",
            variable=self.require_colon, style="Big.TCheckbutton"
        )
        require_colon_check.grid(row=3, column=0, columnspan=4, sticky="w", pady=(6, 0))

        # Second row: double spacing option
        self.double_space = tk.BooleanVar(value=False)
        double_space_check = ttk.Checkbutton(
            container, text="Double spacing (leave one blank line for each new line)",
            variable=self.double_space, style="Big.TCheckbutton"
        )
        double_space_check.grid(row=4, column=0, columnspan=4, sticky="w", pady=(6, 0))

        # Large text box (shift to row 5)
        text_frame = ttk.Frame(container)
        text_frame.grid(row=5, column=0, columnspan=4, sticky="nsew", pady=(12, 0))
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)

        self.text = tk.Text(text_frame, wrap="word", undo=True, height=22)
        self.text.grid(row=0, column=0, sticky="nsew")
        self.text.configure(font=("Arial", 12))  # Larger font in text box

        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=self.text.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.text.configure(yscrollcommand=scrollbar.set)

        # Footer label (shifted to row 6)
        tip = ttk.Label(
            container,
            text="Author Edison Xu Pingzhang (pingzhangxu@gmail.com) Thanks for using!",
            foreground="red", style="Big.TLabel"
        )
        tip.grid(row=6, column=0, columnspan=4, sticky="w", pady=(8, 0))

    def empty(self):
        self.text.delete("1.0", "end")
        self.filename_entry.delete(0, "end")
        self.filename_entry.focus_set()
        self.double_space.set(False)
        self.require_colon.set(False)

    # Generate a non-conflicting file path
    def next_available_path(self, directory: str, stem: str, ext: str) -> str:
        try:
            existing_lower = {name.lower() for name in os.listdir(directory)}
        except Exception:
            existing_lower = set()

        def make_name(i: int) -> str:
            suffix = "" if i == 1 else f"({i})"
            return f"{stem}{suffix}{ext}"

        i = 1
        while True:
            candidate = os.path.join(directory, make_name(i))
            cand_lower = os.path.basename(candidate).lower()
            if cand_lower not in existing_lower and not os.path.exists(candidate):
                return candidate
            i += 1

    def sanitize_stem(self, name: str) -> str:
        name = name.strip()
        name = os.path.basename(name)
        name, _ext = os.path.splitext(name)
        name = re.sub(r'[\\/:*?"<>|]', "", name)
        name = name.strip(" .")
        if len(name) > 100:
            name = name[:100]
        return name

    def clean_text(self, raw: str) -> str:
        # 1) Pre-clean each line
        lines = raw.splitlines()
        cleaned_lines = []
        for line in lines:
            s = line.strip()
            if not s:
                continue
            if re.fullmatch(r"已思考\s*\d+\s*s", s):
                continue
            # Discard lines that are only numbers (but keep "number." style)
            if re.fullmatch(r"""
                ^\s*
                (?:[\(\[]?\d+[\)\]]|\d+)
                \s*[\、\)\:：]?
                \s*$
            """, s, flags=re.X):
                continue
            # Remove leading number — but keep "number."
            if not re.match(r"^\d+\.\s*", s):
                s = re.sub(r"""
                    ^\s*
                    (?:[\(\[]?\d+[\)\]]|\d+)
                    \s*[\、\)\:：-]?
                    \s*
                """, "", s, flags=re.X)
            if s:
                cleaned_lines.append(s)

        # 2) Merge into one line
        text_joined = " ".join(cleaned_lines)

        # 3) Normalize spaces around punctuation
        text_joined = re.sub(r"\s+([，。；：！？、」』》）\]\}%\.,;:!\?\)])", r"\1", text_joined)
        text_joined = re.sub(r"([（「『《\(\[\{])\s+", r"\1", text_joined)
        text_joined = re.sub(r"[ \t]+", " ", text_joined)

        # 4) Insert newlines before headers
        header_pat = re.compile(
            r"([。．\.，,！!？\?；;])\s*"
            r"([\w\u4e00-\u9fff（）()【】《》「」『』／/\- ]{1,80}[：:])"
        )
        text_joined = header_pat.sub(r"\1\n\2", text_joined)

        # 5) Do not break line after colon by default; only break after the first header colon
        text_joined = re.sub(r"([：:])\s*", r"\1 ", text_joined)
        first_header_colon_at_start = re.compile(
            r"^([\w\u4e00-\u9fff（）()【】《》「」『』／/\- ]{1,80}[：:])\s",
            flags=re.M
        )
        text_joined = first_header_colon_at_start.sub(r"\1\n", text_joined, count=1)

        # 6) Line-level cleanup
        lines2 = [ln.rstrip() for ln in text_joined.splitlines()]
        lines2 = [ln for ln in lines2 if ln.strip() != ""]

        # 7) Rule A: Insert newline before "number." (not decimal), keep number.
        joined = "\n".join(lines2)
        joined = re.sub(
            r"(?<!\d)(\d+)\.\s*(?=[^\d])",  # "number." not followed by another digit
            r"\n\1. ",                      # insert newline before
            joined
        )
        lines2 = [ln for ln in joined.splitlines() if ln.strip() != ""]
        # 7.1) Remove isolated number-only lines (e.g. "2.")
        lines2 = [ln for ln in lines2 if not re.match(r'^\s*\d+\.\s*$', ln)]

        # 8) Rule B: Auto-number only header lines (ending with colon); anchored after first numeric line
        numbered_lines = []
        auto_idx = 1
        first_numeric_line = None
        for i, ln in enumerate(lines2):
            if re.match(r"^\d+\.\s+", ln):
                first_numeric_line = i
                break

        for i, line in enumerate(lines2):
            if re.match(r"^\d+\.\s+", line):
                numbered_lines.append(line)  # Keep existing numbering
                continue
            is_title = line.rstrip().endswith("：") or line.rstrip().endswith(":")
            after_anchor = (first_numeric_line is None) or (i >= first_numeric_line)
            if is_title and after_anchor:
                numbered_lines.append(f"{auto_idx}. {line}")
                auto_idx += 1
            else:
                numbered_lines.append(line)

        text_final = "\n".join(numbered_lines).strip()

        # 9) Normalize numbering: re-sequence "number. content" to 1,2,3…
        lines_norm = text_final.splitlines()
        expected = 1
        for i, ln in enumerate(lines_norm):
            m = re.match(r'^(\s*)(\d+)\.\s+(.*\S)\s*$', ln)
            if m:
                prefix, _oldnum, rest = m.groups()
                lines_norm[i] = f"{prefix}{expected}. {rest}"
                expected += 1
        text_final = "\n".join(lines_norm)

        # 10) Remove emoji/unicode symbols
        text_final = re.sub(r"[\U00010000-\U0010FFFF]", "", text_final)

        # 11) Remove spaces between Chinese characters
        text_final = re.sub(r'(?<=[\u4e00-\u9fff])\s+(?=[\u4e00-\u9fff])', '', text_final)

        # 12) Remove bullet symbols (•, ‧, ∙, ·, ●, ▪, ▫, ◦, ﹒,  etc.)
        text_final = re.sub(r"[•‧∙·●▪▫◦﹒]", "", text_final)

        # 13) Double spacing: insert extra blank line before numbered items
        if self.double_space.get():
            text_final = re.sub(r'(^|\n)(\d+\.\s+)', r'\1\n\2', text_final)

        return text_final

    def start_edit(self):
        # If not checked "Already required colon", block and warn
        if not self.require_colon.get():
            messagebox.showwarning("Please check first",
                                   "Please require GPT to add colon after each subtitle, then check the first box!")
            return

        raw = self.text.get("1.0", "end")
        cleaned = self.clean_text(raw)

        # Fill back into text box
        self.text.delete("1.0", "end")
        self.text.insert("1.0", cleaned)

        save_dir = os.getcwd()
        raw_name = self.filename_entry.get()
        stem = self.sanitize_stem(raw_name)
        if not stem:
            stem = "converted"

        try:
            if HAS_DOCX:
                docx_path = self.next_available_path(save_dir, stem, ".docx")
                doc = Document()
                for line in cleaned.splitlines():
                    doc.add_paragraph(line)
                doc.save(docx_path)
                messagebox.showinfo("Saved", f"Saved as DOCX:\n{docx_path}")
            else:
                txt_path = self.next_available_path(save_dir, stem, ".txt")
                with open(txt_path, "w", encoding="utf-8") as f:
                    f.write(cleaned)
                messagebox.showinfo(
                    "python-docx not detected! Saved as TXT",
                    f"Saved as TXT:\n{txt_path}\n\n"
                    "If you want to save as .docx, please install: pip install python-docx"
                )
        except Exception as e:
            messagebox.showerror("Save failed", f"Error occurred: {e}")

if __name__ == '__main__':
    root = tk.Tk()
    app = GPTTextEditApp(root)
    root.mainloop()
