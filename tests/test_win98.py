"""Selbsttest am PC: python tests/test_win98.py"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "device"))
from clippy.win98 import wrap

assert wrap("aa bb cc", 5, len) == ["aa bb", "cc"]
assert wrap("einsehrlangeswort kurz", 5, len) == ["einsehrlangeswort", "kurz"]  # ein Wort wird nie zerteilt
assert wrap("", 5, len) == [""]
assert wrap("eins\nzwei drei", 9, len) == ["eins", "zwei drei"]  # Zeilenwechsel bleiben
print("ok")
