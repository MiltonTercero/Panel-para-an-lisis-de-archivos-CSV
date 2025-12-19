"""
Custom dialog utilities for EDA Panel Application.
Provides styled message boxes and confirmation dialogs.
"""

import customtkinter as ctk
from typing import Optional, Callable


class CustomDialog(ctk.CTkToplevel):
    """Base class for custom dialogs."""
    
    def __init__(
        self,
        parent,
        title: str,
        message: str,
        dialog_type: str = "info",
        width: int = 400,
        height: int = 200
    ):
        super().__init__(parent)
        
        self.title(title)
        self.geometry(f"{width}x{height}")
        self.resizable(False, False)
        
        # Center on parent
        self.transient(parent)
        self.grab_set()
        
        # Colors by type
        colors = {
            "info": ("#3498db", "ℹ️"),
            "success": ("#2ecc71", "✓"),
            "warning": ("#f39c12", "⚠"),
            "error": ("#e74c3c", "✕")
        }
        
        color, icon = colors.get(dialog_type, colors["info"])
        
        # Content frame
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Icon and title
        header_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 15))
        
        icon_label = ctk.CTkLabel(
            header_frame,
            text=icon,
            font=ctk.CTkFont(size=32),
            text_color=color
        )
        icon_label.pack(side="left", padx=(0, 10))
        
        title_label = ctk.CTkLabel(
            header_frame,
            text=title,
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=color
        )
        title_label.pack(side="left")
        
        # Message
        message_label = ctk.CTkLabel(
            self.content_frame,
            text=message,
            font=ctk.CTkFont(size=13),
            wraplength=width - 60,
            justify="left"
        )
        message_label.pack(fill="x", pady=(0, 20))
        
        # OK button
        ok_button = ctk.CTkButton(
            self.content_frame,
            text="Aceptar",
            command=self.destroy,
            fg_color=color,
            hover_color=self._darken_color(color),
            width=100
        )
        ok_button.pack()
        
        # Bind escape key
        self.bind("<Escape>", lambda e: self.destroy())
        self.bind("<Return>", lambda e: self.destroy())
        
        # Center window
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - width) // 2
        y = parent.winfo_y() + (parent.winfo_height() - height) // 2
        self.geometry(f"+{x}+{y}")
        
        self.focus_force()
    
    def _darken_color(self, hex_color: str) -> str:
        """Darken a hex color."""
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        darkened = tuple(max(0, int(c * 0.8)) for c in rgb)
        return f"#{darkened[0]:02x}{darkened[1]:02x}{darkened[2]:02x}"


class ConfirmDialog(ctk.CTkToplevel):
    """Confirmation dialog with Yes/No buttons."""
    
    def __init__(
        self,
        parent,
        title: str,
        message: str,
        on_confirm: Optional[Callable] = None,
        on_cancel: Optional[Callable] = None,
        width: int = 400,
        height: int = 180
    ):
        super().__init__(parent)
        
        self.on_confirm = on_confirm
        self.on_cancel = on_cancel
        self.result = False
        
        self.title(title)
        self.geometry(f"{width}x{height}")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        # Content
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Icon
        icon_label = ctk.CTkLabel(
            content_frame,
            text="❓",
            font=ctk.CTkFont(size=32)
        )
        icon_label.pack(pady=(0, 10))
        
        # Message
        message_label = ctk.CTkLabel(
            content_frame,
            text=message,
            font=ctk.CTkFont(size=13),
            wraplength=width - 60,
            justify="center"
        )
        message_label.pack(fill="x", pady=(0, 20))
        
        # Buttons
        button_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        button_frame.pack()
        
        cancel_button = ctk.CTkButton(
            button_frame,
            text="Cancelar",
            command=self._on_cancel,
            fg_color="#6c757d",
            hover_color="#5a6268",
            width=100
        )
        cancel_button.pack(side="left", padx=5)
        
        confirm_button = ctk.CTkButton(
            button_frame,
            text="Confirmar",
            command=self._on_confirm,
            fg_color="#2ecc71",
            hover_color="#27ae60",
            width=100
        )
        confirm_button.pack(side="left", padx=5)
        
        # Bind keys
        self.bind("<Escape>", lambda e: self._on_cancel())
        self.bind("<Return>", lambda e: self._on_confirm())
        
        # Center
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - width) // 2
        y = parent.winfo_y() + (parent.winfo_height() - height) // 2
        self.geometry(f"+{x}+{y}")
        
        self.focus_force()
    
    def _on_confirm(self):
        self.result = True
        if self.on_confirm:
            self.on_confirm()
        self.destroy()
    
    def _on_cancel(self):
        self.result = False
        if self.on_cancel:
            self.on_cancel()
        self.destroy()


# Convenience functions
def show_info(parent, title: str, message: str):
    """Show info dialog."""
    dialog = CustomDialog(parent, title, message, "info")
    parent.wait_window(dialog)


def show_success(parent, title: str, message: str):
    """Show success dialog."""
    dialog = CustomDialog(parent, title, message, "success")
    parent.wait_window(dialog)


def show_warning(parent, title: str, message: str):
    """Show warning dialog."""
    dialog = CustomDialog(parent, title, message, "warning")
    parent.wait_window(dialog)


def show_error(parent, title: str, message: str):
    """Show error dialog."""
    dialog = CustomDialog(parent, title, message, "error")
    parent.wait_window(dialog)


def show_confirm(parent, title: str, message: str) -> bool:
    """Show confirmation dialog and return result."""
    dialog = ConfirmDialog(parent, title, message)
    parent.wait_window(dialog)
    return dialog.result
