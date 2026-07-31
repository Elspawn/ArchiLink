import re
from typing import Iterable

ANSI_ESCAPE = re.compile(r"\x1b\[[0-9;]*m")

def strip_ansi(text: str) -> str:
    return ANSI_ESCAPE.sub("", text)

class AnsiText:
    """
    Transparent wrapper for text with ANSI color codes. 
    Provides methods to get the visible length of the text, render it with color codes,
    and left-justify it while considering the visible length.
    """
    RESET = "\u001b[0m"

    def __init__(self, text: str, color: str | None = None):
        self.text = str(text)
        self.color = color

    def visible_length(self) -> int:
        return len(self.text)

    def render(self) -> str:
        if self.color is None:
            return self.text

        return f"\u001b[0;{self.color}m{self.text}{self.RESET}"

    def ljust(self, width: int) -> str:
        rendered = self.render()
        padding = width - len(strip_ansi(rendered))
        return rendered + " " * max(0, padding)

    def __str__(self):
        return self.render()
    
class AnsiTable:
    DISCORD_LIMIT = 1800
    def __init__(self, headers: list[str], title: str | None = None):
        self.headers = headers
        self.title = title
        self.rows: list[list[AnsiText]] = []

    def add_row(self, *cells):
        row = []
        for cell in cells:
            if isinstance(cell, AnsiText):
                row.append(cell)
            else:
                row.append(AnsiText(str(cell)))
        self.rows.append(row)

    def _column_widths(self):
        widths = [len(h) for h in self.headers]
        for row in self.rows:
            for i, cell in enumerate(row):
                widths[i] = max(widths[i], cell.visible_length())
        return [w + 1 for w in widths]

    def _render_lines(self):
        widths = self._column_widths()
        lines = []
        if self.title:
            lines.append(self.title)
            lines.append("")
        header = " || ".join(
            h.ljust(widths[i])
            for i, h in enumerate(self.headers)
        )
        lines.append(header)
        for row in self.rows:
            line = " || ".join(
                cell.ljust(widths[i])
                for i, cell in enumerate(row)
            )
            lines.append(line)
        return lines

    async def send(self, destination):
        msg = "```ansi\n"
        for line in self._render_lines():
            if len(msg) + len(strip_ansi(line)) > self.DISCORD_LIMIT:
                msg += "```"
                await destination.send(msg)
                msg = "```ansi\n"
            msg += line + "\n"
        msg += "```"
        if msg != "```ansi\n```":
            await destination.send(msg)
            
