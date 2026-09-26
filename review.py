#!/usr/bin/env python3
"""便捷入口：`python review.py <路径>` 等价于 `python -m cra review <路径>`。

也支持直接透传子命令：`python review.py chat examples`、`python review.py web`。
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cra.cli import main  # noqa: E402  (需要先补 sys.path)

SUBCOMMANDS = {"review", "scan", "chat", "web"}


def run() -> int:
    argv = sys.argv[1:]
    if argv and argv[0] in SUBCOMMANDS:
        return main(argv)
    return main(["review", *argv])


if __name__ == "__main__":
    raise SystemExit(run())
