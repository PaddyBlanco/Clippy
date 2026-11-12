"""Selbsttest am PC: python tests/test_bubble.py"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "device"))
from clippy.pet.bubble import wrap

assert wrap("aa bb cc", 5, len) == ["aa bb", "cc"]
assert wrap("einsehrlangeswort kurz", 5, len) == ["einsehrlangeswort", "kurz"]  # ein Wort wird nie zerteilt
assert wrap("", 5, len) == [""]
print("ok")
