"""Interface to :mod:`re`."""

import re
import sre_compile  # noqa: I201

# pylint: disable=invalid-name
Pattern = getattr(re, 'Pattern', type(sre_compile.compile('', 0)))
Match = getattr(re, 'Match', type(sre_compile.compile('', 0).match('')))
