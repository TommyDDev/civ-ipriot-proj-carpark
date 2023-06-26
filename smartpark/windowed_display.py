import tkinter as tk
from typing import Iterable


class WindowedDisplay:

    DISPLAY_INIT = '– – –'
    SEP = ':'

    def __init__(self, title: str, display_fields: Iterable[str]):

        self.window = tk.Tk()
        self.window.title(f'{title}: Parking')
        self.window.geometry('800x400')
        self.window.resizable(False, False)
        self.display_fields = display_fields

        self.gui_elements = {}
        for i, field in enumerate(self.display_fields):
            self.gui_elements[f'lbl_field_{i}'] = tk.Label(
                self.window, text=field + self.SEP, font=('Arial', 50))
            self.gui_elements[f'lbl_value_{i}'] = tk.Label(
                self.window, text=self.DISPLAY_INIT, font=('Arial', 50))

            self.gui_elements[f'lbl_field_{i}'].grid(
                row=i, column=0, sticky=tk.E, padx=5, pady=5)
            self.gui_elements[f'lbl_value_{i}'].grid(
                row=i, column=1, sticky=tk.W, padx=10)

    def show(self):
        self.window.mainloop()

    def update(self, updated_values):
        for field_name, field_value in updated_values.items():
            for widget_name, widget in self.gui_elements.items():
                if widget_name.startswith('lbl_field_') and widget.cget('text').strip(self.SEP).strip() == field_name:
                    value_widget_name = widget_name.replace('lbl_field_', 'lbl_value_')
                    if value_widget_name in self.gui_elements:
                        self.gui_elements[value_widget_name].config(text=field_value)
