"""
NUX Agent — Response Formatter
Terminal UI formatting utilities.
"""

import textwrap
import shutil
import time

# Terminal colors
G  = "\033[92m"   # green
DG = "\033[32m"   # dark green
CY = "\033[96m"   # cyan
RD = "\033[91m"   # red
GR = "\033[90m"   # gray
YL = "\033[93m"   # yellow
BL = "\033[1m"    # bold
RS = "\033[0m"    # reset


def tw() -> int:
    """Get terminal width, capped at 70."""
    return min(shutil.get_terminal_size().columns, 70)


def print_user(text: str):
    """Print user message in cyan box."""
    w = min(tw(), 60)
    print(f"\n{CY}┌─ YOU{RS}")
    for line in textwrap.wrap(text, w - 4) or [text]:
        print(f"{CY}│{RS}  {line}")
    print(f"{CY}└{'─' * (w-1)}{RS}")


def print_nux(text: str):
    """Print NUX response in green box."""
    w = min(tw(), 60)
    print(f"\n{G}┌─ NUX ⚡{RS}")
    for line in text.strip().split("\n"):
        if line.strip() == "":
            print(f"{G}│{RS}")
        else:
            for wrapped in textwrap.wrap(line, w - 4) or [""]:
                print(f"{G}│{RS}  {wrapped}")
    print(f"{G}└{'─' * (w-1)}{RS}\n")


def print_thinking():
    """Animated thinking spinner."""
    frames = ["⠋","⠙","⠹","⠸","⠼","⠴","⠦","⠧","⠇","⠏"]
    for i in range(12):
        print(f"\r{G}  {frames[i % len(frames)]}{RS}{GR} nux is cooking...{RS}", end="", flush=True)
        time.sleep(0.08)
    print("\r" + " " * 30 + "\r", end="", flush=True)


def divider():
    """Print a horizontal divider."""
    print(f"{GR}{'─' * min(tw(), 60)}{RS}")
