import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk

from services.config_service import get_api_key, save_api_key
from services.medication_parser import Medication, extract_medications_from_docx, format_medications


APP_TITLE = "MedInUse"

BG = "#6f7b80"
SURFACE = "#eef3f4"
DARK = "#222a33"
TEXT = "#1f272c"
MUTED = "#6d797f"
ACCENT = "#f3ff00"
ACCENT_HOVER = "#dbe600"
WHITE = "#f8fbfb"


class MainWindow(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        ctk.set_appearance_mode("light")

        self.title(APP_TITLE)
        self.geometry("900x640")
        self.minsize(780, 560)
        self.configure(fg_color=BG)

        self.selected_file = tk.StringVar()
        self.format_mode = tk.StringVar(value="Uma por linha")
        self.medication_count = tk.StringVar(value="0 medicações")
        self.status_text = tk.StringVar(value="Escolha um arquivo DOCX para começar.")
        self.current_medications: list[Medication] = []
        self._review_result: list[Medication] = []

        self._build_layout()
        self._refresh_api_label()

    def _build_layout(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=26, pady=(22, 12))
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkButton(
            header,
            text="<",
            width=38,
            height=38,
            corner_radius=19,
            fg_color=SURFACE,
            hover_color=WHITE,
            text_color=TEXT,
            font=("Segoe UI", 18),
            command=self._clear_output,
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkButton(
            header,
            text="Chave API",
            width=96,
            height=34,
            corner_radius=17,
            fg_color=SURFACE,
            hover_color=WHITE,
            text_color=TEXT,
            font=("Segoe UI", 12),
            command=self._configure_api_key,
        ).grid(row=0, column=1, sticky="e", padx=(10, 0))

        ctk.CTkLabel(header, text="MedInUse", text_color=WHITE, font=("Segoe UI", 30)).grid(
            row=1, column=0, columnspan=2, sticky="w", pady=(12, 0)
        )
        ctk.CTkLabel(
            header,
            text="Transforme prescrições em uma lista limpa para copiar.",
            text_color="#e8eeee",
            font=("Segoe UI", 14),
        ).grid(row=2, column=0, columnspan=2, sticky="w", pady=(2, 0))

        content = ctk.CTkFrame(self, fg_color="transparent")
        content.grid(row=1, column=0, sticky="nsew", padx=26, pady=(0, 22))
        content.grid_columnconfigure(0, weight=0, minsize=300)
        content.grid_columnconfigure(1, weight=1)
        content.grid_rowconfigure(0, weight=1)

        left = ctk.CTkFrame(content, fg_color=DARK, corner_radius=8)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 14))
        left.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(left, text="Arquivo", text_color=WHITE, font=("Segoe UI", 20)).grid(
            row=0, column=0, sticky="w", padx=18, pady=(18, 8)
        )

        file_card = ctk.CTkFrame(left, fg_color=SURFACE, corner_radius=8)
        file_card.grid(row=1, column=0, sticky="ew", padx=14, pady=(0, 12))
        file_card.grid_columnconfigure(0, weight=1)

        self.file_name_label = ctk.CTkLabel(
            file_card,
            text="Nenhum DOCX selecionado",
            text_color=TEXT,
            font=("Segoe UI", 14, "bold"),
            anchor="w",
        )
        self.file_name_label.grid(row=0, column=0, sticky="ew", padx=14, pady=(14, 0))

        self.file_path_label = ctk.CTkLabel(
            file_card,
            text="",
            text_color=MUTED,
            font=("Segoe UI", 11),
            anchor="w",
            wraplength=240,
        )
        self.file_path_label.grid(row=1, column=0, sticky="ew", padx=14, pady=(2, 12))

        ctk.CTkButton(
            file_card,
            text="Escolher DOCX",
            height=38,
            corner_radius=8,
            fg_color=ACCENT,
            hover_color=ACCENT_HOVER,
            text_color=TEXT,
            font=("Segoe UI", 13, "bold"),
            command=self._select_file,
        ).grid(row=2, column=0, sticky="ew", padx=14, pady=(0, 14))

        ctk.CTkLabel(left, text="Formato", text_color=WHITE, font=("Segoe UI", 20)).grid(
            row=2, column=0, sticky="w", padx=18, pady=(6, 8)
        )

        self.format_control = ctk.CTkSegmentedButton(
            left,
            values=["Uma por linha", "Linha única"],
            variable=self.format_mode,
            command=lambda _value: self._refresh_format(),
            height=38,
            corner_radius=8,
            fg_color="#4b5660",
            selected_color=ACCENT,
            selected_hover_color=ACCENT_HOVER,
            unselected_color="#4b5660",
            unselected_hover_color="#5a666f",
            text_color=TEXT,
            font=("Segoe UI", 12, "bold"),
        )
        self.format_control.grid(row=3, column=0, sticky="ew", padx=14, pady=(0, 14))

        info_card = ctk.CTkFrame(left, fg_color="#161d25", corner_radius=8)
        info_card.grid(row=4, column=0, sticky="ew", padx=14, pady=(6, 14))
        info_card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(info_card, textvariable=self.medication_count, text_color=ACCENT, font=("Segoe UI", 24)).grid(
            row=0, column=0, sticky="w", padx=14, pady=(12, 0)
        )
        ctk.CTkLabel(
            info_card,
            textvariable=self.status_text,
            text_color="#d7dee2",
            font=("Segoe UI", 12),
            wraplength=235,
            justify="left",
            anchor="w",
        ).grid(row=1, column=0, sticky="ew", padx=14, pady=(2, 14))

        self.api_status = ctk.CTkLabel(left, text="", text_color="#d7dee2", font=("Segoe UI", 11), anchor="w")
        self.api_status.grid(row=5, column=0, sticky="ew", padx=18, pady=(0, 14))

        preview = ctk.CTkFrame(content, fg_color=SURFACE, corner_radius=8)
        preview.grid(row=0, column=1, sticky="nsew")
        preview.grid_columnconfigure(0, weight=1)
        preview.grid_rowconfigure(1, weight=1)

        top = ctk.CTkFrame(preview, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", padx=18, pady=(18, 10))
        top.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(top, text="Lista para copiar", text_color=TEXT, font=("Segoe UI", 22)).grid(row=0, column=0, sticky="w")
        ctk.CTkButton(top, text="Ler arquivo", width=96, height=34, corner_radius=8, fg_color="#d8e0e2", hover_color="#c8d2d5", text_color=TEXT, command=self._process_selected_file).grid(row=0, column=1, padx=(8, 0))
        ctk.CTkButton(top, text="Revisar", width=96, height=34, corner_radius=8, fg_color="#d8e0e2", hover_color="#c8d2d5", text_color=TEXT, command=self._review_current_medications).grid(row=0, column=2, padx=(8, 0))
        ctk.CTkButton(top, text="Copiar", width=96, height=34, corner_radius=8, fg_color=ACCENT, hover_color=ACCENT_HOVER, text_color=TEXT, font=("Segoe UI", 13, "bold"), command=self._copy_output).grid(row=0, column=3, padx=(8, 0))

        self.output = ctk.CTkTextbox(
            preview,
            wrap="word",
            font=("Segoe UI", 15),
            fg_color=WHITE,
            text_color=TEXT,
            corner_radius=8,
            border_width=0,
        )
        self.output.grid(row=1, column=0, sticky="nsew", padx=18, pady=(0, 18))
        self.output.insert("1.0", "A lista aparecerá aqui depois de selecionar um arquivo.")

    def _select_file(self) -> None:
        file_path = filedialog.askopenfilename(
            title="Escolha o arquivo DOCX",
            filetypes=[("Documentos Word", "*.docx"), ("Todos os arquivos", "*.*")],
        )
        if not file_path:
            return

        self.selected_file.set(file_path)
        path = Path(file_path)
        self.file_name_label.configure(text=path.name)
        self.file_path_label.configure(text=str(path.parent))
        self._process_selected_file()

    def _process_selected_file(self) -> None:
        file_path = self.selected_file.get()
        if not file_path:
            return

        try:
            medications = extract_medications_from_docx(Path(file_path))
        except Exception as exc:
            messagebox.showerror("Não foi possível ler o arquivo", f"Confira se o arquivo DOCX está fechado e tente de novo.\n\nDetalhe: {exc}")
            return

        self.current_medications = medications
        self.medication_count.set(f"{len(medications)} medicação" if len(medications) == 1 else f"{len(medications)} medicações")

        if not medications:
            self.status_text.set("Não identifiquei medicações no arquivo selecionado.")
            self._set_output("Nenhuma medicação foi identificada. Confira se cada medicação está seguida pela posologia no arquivo.")
            return

        if self._has_unknown_schedule(medications):
            self.current_medications = self._review_medications(medications)

        self.status_text.set(self._status_for_medications())
        self._render_current_medications()

    def _refresh_format(self) -> None:
        if self.current_medications:
            self._render_current_medications()

    def _render_current_medications(self) -> None:
        result = format_medications(self.current_medications, self.format_mode.get() == "Uma por linha")
        self._set_output(result)

    def _set_output(self, text: str) -> None:
        self.output.delete("1.0", tk.END)
        self.output.insert("1.0", text)

    def _has_unknown_schedule(self, medications: list[Medication] | None = None) -> bool:
        items = medications if medications is not None else self.current_medications
        return any(medication.schedule == "conferir posologia" for medication in items)

    def _status_for_medications(self) -> str:
        if self._has_unknown_schedule():
            return "Há posologias para revisar antes de copiar."
        return "Lista pronta. Revise rapidamente antes de copiar."

    def _review_current_medications(self) -> None:
        if not self.current_medications:
            messagebox.showinfo("Nada para revisar", "Gere uma lista antes de revisar.")
            return

        self.current_medications = self._review_medications(self.current_medications, include_all=True)
        self.status_text.set(self._status_for_medications())
        self._render_current_medications()

    def _review_medications(self, medications: list[Medication], include_all: bool = False) -> list[Medication]:
        targets = [
            (index, medication)
            for index, medication in enumerate(medications)
            if include_all or medication.schedule == "conferir posologia"
        ]
        if not targets:
            return medications

        dialog = ctk.CTkToplevel(self)
        dialog.title("Revisar posologias")
        dialog.geometry("620x420")
        dialog.minsize(560, 340)
        dialog.configure(fg_color=BG)
        dialog.transient(self)
        dialog.grab_set()

        frame = ctk.CTkFrame(dialog, fg_color=SURFACE, corner_radius=8)
        frame.pack(fill="both", expand=True, padx=18, pady=18)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(frame, text="Revisar posologias", text_color=TEXT, font=("Segoe UI", 22)).grid(
            row=0, column=0, sticky="w", padx=16, pady=(16, 2)
        )
        ctk.CTkLabel(
            frame,
            text="Edite apenas o que precisar. Exemplos: 1-0-1, 1x/dia, 1 comp. semana/12 semanas.",
            text_color=MUTED,
            font=("Segoe UI", 12),
            anchor="w",
            wraplength=540,
        ).grid(row=1, column=0, sticky="ew", padx=16, pady=(0, 10))

        list_frame = ctk.CTkScrollableFrame(frame, fg_color=WHITE, corner_radius=8)
        list_frame.grid(row=2, column=0, sticky="nsew", padx=16, pady=(0, 12))
        list_frame.grid_columnconfigure(1, weight=1)

        entries: dict[int, ctk.CTkEntry] = {}
        for row, (index, medication) in enumerate(targets):
            ctk.CTkLabel(
                list_frame,
                text=medication.name,
                text_color=TEXT,
                font=("Segoe UI", 13, "bold"),
                anchor="w",
                wraplength=230,
            ).grid(row=row, column=0, sticky="ew", padx=(10, 8), pady=8)

            value = "" if medication.schedule == "conferir posologia" else medication.schedule
            entry = ctk.CTkEntry(list_frame, height=34, corner_radius=8)
            entry.insert(0, value)
            entry.grid(row=row, column=1, sticky="ew", padx=(0, 10), pady=8)
            entries[index] = entry

        self._review_result = medications

        def apply_review() -> None:
            updated = list(medications)
            for index, entry in entries.items():
                value = entry.get().strip()
                if value:
                    updated[index] = Medication(updated[index].name, value)
            self._review_result = updated
            dialog.destroy()

        buttons = ctk.CTkFrame(frame, fg_color="transparent")
        buttons.grid(row=3, column=0, sticky="e", padx=16, pady=(0, 16))
        ctk.CTkButton(buttons, text="Agora não", width=104, fg_color="#d8e0e2", hover_color="#c8d2d5", text_color=TEXT, command=dialog.destroy).pack(side="left", padx=(0, 8))
        ctk.CTkButton(buttons, text="Aplicar", width=104, fg_color=ACCENT, hover_color=ACCENT_HOVER, text_color=TEXT, command=apply_review).pack(side="left")

        self.wait_window(dialog)
        return self._review_result

    def _copy_output(self) -> None:
        content = self.output.get("1.0", tk.END).strip()
        if not content or content.startswith("A lista aparecerá"):
            messagebox.showinfo("Nada para copiar", "Gere uma lista antes de copiar.")
            return

        self.clipboard_clear()
        self.clipboard_append(content)
        self.update()
        self.status_text.set("Lista copiada para a área de transferência.")

    def _clear_output(self) -> None:
        self.selected_file.set("")
        self.current_medications = []
        self.file_name_label.configure(text="Nenhum DOCX selecionado")
        self.file_path_label.configure(text="")
        self.medication_count.set("0 medicações")
        self.status_text.set("Escolha um arquivo DOCX para começar.")
        self._set_output("A lista aparecerá aqui depois de selecionar um arquivo.")

    def _configure_api_key(self) -> None:
        dialog = ctk.CTkToplevel(self)
        dialog.title("Configurar chave da API")
        dialog.geometry("460x220")
        dialog.resizable(False, False)
        dialog.configure(fg_color=BG)
        dialog.transient(self)
        dialog.grab_set()

        frame = ctk.CTkFrame(dialog, fg_color=SURFACE, corner_radius=8)
        frame.pack(fill="both", expand=True, padx=18, pady=18)

        ctk.CTkLabel(frame, text="Chave da API", text_color=TEXT, font=("Segoe UI", 18)).pack(anchor="w", padx=16, pady=(16, 4))
        api_key = tk.StringVar(value=get_api_key())
        entry = ctk.CTkEntry(frame, textvariable=api_key, show="*", height=38, corner_radius=8)
        entry.pack(fill="x", padx=16, pady=(0, 8))

        ctk.CTkLabel(
            frame,
            text="Opcional para este app. A extração do DOCX funciona sem chave.",
            text_color=MUTED,
            font=("Segoe UI", 12),
        ).pack(anchor="w", padx=16)

        buttons = ctk.CTkFrame(frame, fg_color="transparent")
        buttons.pack(anchor="e", padx=16, pady=(18, 0))
        ctk.CTkButton(buttons, text="Cancelar", width=92, fg_color="#d8e0e2", hover_color="#c8d2d5", text_color=TEXT, command=dialog.destroy).pack(side="left", padx=(0, 8))
        ctk.CTkButton(buttons, text="Salvar", width=92, fg_color=ACCENT, hover_color=ACCENT_HOVER, text_color=TEXT, command=lambda: self._save_api_key(dialog, api_key.get())).pack(side="left")

        entry.focus_set()
        self.wait_window(dialog)

    def _save_api_key(self, dialog: ctk.CTkToplevel, api_key: str) -> None:
        save_api_key(api_key)
        dialog.destroy()
        self._refresh_api_label()
        self.status_text.set("Chave salva nas configurações do usuário.")

    def _refresh_api_label(self) -> None:
        status = "API configurada" if get_api_key() else "API opcional não configurada"
        self.api_status.configure(text=status)


def main() -> None:
    app = MainWindow()
    app.mainloop()
