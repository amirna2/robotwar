"""
SOLID-based terminal output system for consistent UI formatting.

This module provides a clean, reusable interface for terminal output that follows
SOLID principles. It separates concerns between terminal sizing, text formatting,
and output rendering.
"""

import shutil
from abc import ABC, abstractmethod
from typing import Optional
from colorama import Style


class TerminalSizer:
    """Single Responsibility: Handle terminal size detection and calculations."""
    
    @staticmethod
    def get_terminal_width() -> int:
        """Get current terminal width with fallback."""
        try:
            return shutil.get_terminal_size().columns
        except OSError:
            return 80  # Fallback width
    
    @staticmethod
    def calculate_center_padding(text: str, terminal_width: Optional[int] = None) -> int:
        """Calculate padding needed to center text."""
        if terminal_width is None:
            terminal_width = TerminalSizer.get_terminal_width()
        
        # Strip ANSI color codes for accurate length calculation
        clean_text = text
        if '\033[' in text:
            import re
            clean_text = re.sub(r'\033\[[0-9;]*m', '', text)
        
        padding = max(0, (terminal_width - len(clean_text)) // 2)
        return padding


class TextFormatter:
    """Single Responsibility: Handle text formatting and styling."""
    
    @staticmethod
    def center_text(text: str, terminal_width: Optional[int] = None) -> str:
        """Center text within terminal width."""
        padding = TerminalSizer.calculate_center_padding(text, terminal_width)
        return ' ' * padding + text
    
    @staticmethod
    def apply_color(text: str, color: str) -> str:
        """Apply color to text with proper reset."""
        return f"{color}{text}{Style.RESET_ALL}"


class OutputRenderer(ABC):
    """Interface Segregation: Abstract interface for different output types."""
    
    @abstractmethod
    def render(self, text: str, color: Optional[str] = None) -> None:
        """Render text to output."""
        pass


class CenteredOutputRenderer(OutputRenderer):
    """Concrete implementation: Renders centered text to terminal."""
    
    def __init__(self, terminal_sizer: TerminalSizer, text_formatter: TextFormatter):
        self.terminal_sizer = terminal_sizer
        self.text_formatter = text_formatter
    
    def render(self, text: str, color: Optional[str] = None) -> None:
        """Render centered text with optional color."""
        centered_text = self.text_formatter.center_text(text)
        
        if color:
            output = self.text_formatter.apply_color(centered_text, color)
        else:
            output = centered_text
        
        print(output)


class CenteredInputRenderer:
    """Single Responsibility: Handle centered input prompts."""
    
    def __init__(self, text_formatter: TextFormatter):
        self.text_formatter = text_formatter
    
    def get_input(self, prompt: str = "") -> str:
        """Get user input with centered prompt."""
        if prompt:
            centered_prompt = self.text_formatter.center_text(prompt)
            return input(centered_prompt)
        else:
            # For empty prompts, center the cursor position
            padding = TerminalSizer.calculate_center_padding("")
            return input(' ' * padding)


class TerminalOutputManager:
    """
    Dependency Inversion: High-level module that coordinates output rendering.
    
    This class serves as the main interface for terminal output operations,
    following the Facade pattern while maintaining SOLID principles.
    """
    
    def __init__(self):
        # Dependency injection of concrete implementations
        self.terminal_sizer = TerminalSizer()
        self.text_formatter = TextFormatter()
        self.output_renderer = CenteredOutputRenderer(self.terminal_sizer, self.text_formatter)
        self.input_renderer = CenteredInputRenderer(self.text_formatter)
    
    def print_centered(self, text: str, color: Optional[str] = None) -> None:
        """Print text centered in terminal."""
        self.output_renderer.render(text, color)
    
    def input_centered(self, prompt: str = "") -> str:
        """Get user input with centered prompt."""
        return self.input_renderer.get_input(prompt)
    
    def clear_screen(self) -> None:
        """Clear terminal screen."""
        import os
        os.system('cls' if os.name == 'nt' else 'clear')