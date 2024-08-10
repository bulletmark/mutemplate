'Implement monitoring for file changes'
# Author: Mark Blakeney, Oct 2023.
from __future__ import annotations

import time
from pathlib import Path

class Watcher:
    'Monitor file changes using simple polling'
    def __init__(self, watching: list[Path], *,
                 log_changes: bool = False,
                 poll_time: float = 0.2) -> None:
        self.files = {f: f.stat().st_mtime for f in watching}
        self.log_changes = log_changes
        self.poll_time = poll_time

    def wait_for_change(self) -> None:
        all_changes = set()
        while True:
            changes = set()
            for file, mtime in self.files.items():
                new_mtime = file.stat().st_mtime
                if new_mtime != mtime:
                    self.files[file] = new_mtime
                    changes.add(file)

            # Return only after we have settled after a change
            if changes:
                all_changes |= changes
            elif all_changes:
                if self.log_changes:
                    for f in all_changes:
                        print(f'Change detected in {f}')
                break

            time.sleep(self.poll_time)
