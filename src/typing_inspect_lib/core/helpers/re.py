import sre_compile
import re

# pylint: disable=invalid-name
Pattern = getattr(re, 'Pattern', type(sre_compile.compile('', 0)))
Match = getattr(re, 'Match', type(sre_compile.compile('', 0).match('')))
