# Retained snapshots: mixed failure and observed-success evidence

- zcode-first-storage-probe preserves the original first storage attempt: exit 1, 1/6 groups passing.
- zcode-python-probe-at-first-observation preserves the first snapshot observed by the dispatcher, which is already the corrected 24/24 successful run, exit 0. It is NOT the earlier 23/24 failed output. The folder name does not classify this successful snapshot as a failure. Unless another actual original file is found, the earlier Python failure remains visible only in task history/self-disclosure, with its standalone output overwritten.
- No later reproduction is presented as an original historical output.
