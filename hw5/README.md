PyShell OS — Simulated Heap Allocator (HW5)

A simulated dynamic memory allocator implemented in Python for CISC 3320 (Operating Systems). This module tracks metadata blocks over a configurable byte pool (0 to size - 1) without storing raw bytes, supporting First-Fit, Best-Fit, and Worst-Fit placement policies, block splitting, immediate neighbor coalescing, and invariant verification.

1. How to Run

Prerequisites

Python 3.x

Execution

Run the interactive shell from your terminal:

# Run with default 1000-byte pool and First-Fit policy
python3 allocator.py

# Run with custom pool size
python3 allocator.py 2000

# Run with custom pool size and initial policy
python3 allocator.py 1000 best-fit


Supported Commands

Command

Description

Example

alloc <name> <size>

Allocates a named block of <size> bytes using the active policy.

alloc A 200

free <name>

Frees an active block by <name> and coalesces adjacent holes.

free A

policy <first|best|worst>

Switches placement strategy dynamically (first, best, worst).

policy best

stats

Displays pool usage, hole count, largest hole, fragmentation, and free list.

stats

map

Displays a detailed table of all allocated and free blocks with byte ranges.

map

visual (or viz)

Prints an ASCII bar visualization (1 char = 10 bytes).

visual

exit

Exits the interactive shell.

exit

2. Design Decisions

Representation

Block Storage: Blocks are stored in a single sorted Python list ordered sequentially by their starting byte address (offset).

Entry Structure: Each element in the list is a dictionary holding four fields:

offset (int): Starting byte address of the block.

size (int): Length of the block in bytes.

is_allocated (bool): True if currently in use, False if it is a free hole.

name (str | None): Identifier assigned during alloc, or None when free.

Search & Tie-Breaking

First-Fit: Iterates from address 0 upward and selects the first free block where size >= requested_size.

Best-Fit: Scans all free blocks to find the block that leaves the smallest non-negative remainder (block_size - requested_size).

Worst-Fit: Scans all free blocks to select the largest available hole.

Tie-Break Rule: When multiple holes tie in Best-Fit or Worst-Fit, the allocator deterministically selects the hole with the lowest starting memory address.

Coalescing

Immediate Coalescing: Whenever free(name) is called, the block's is_allocated flag is set to False and _coalesce() immediately scans the sorted list to merge any adjacent unallocated blocks.

Double-Sided Merging: Because blocks are stored in address order, freeing a block located between two existing free holes merges all three contiguous entries into a single free block in one pass.

Edge Cases & Error Handling

Exact Fit: If requested_size == hole_size, no zero-byte remainder block is created; the existing hole is converted in-place to allocated.

Invalid Requests: Zero/negative sizes, duplicate allocation names, oversized requests (out of memory), unknown block names on free, and double-frees return descriptive error messages and leave the memory pool completely unmodified.

System Invariants

After every alloc and free operation, _check_invariants() asserts:

Conservation of Memory: $\text{Used Bytes} + \text{Free Bytes} = \text{Total Pool Size}$.

Contiguity & No Overlaps: Block $i$'s offset + size strictly equals Block $i+1$'s offset, starting at 0 and ending at total_size.

No Zero-Size Blocks: Every block strictly satisfies size > 0.

3. Fragmentation Metrics & Formulas

The stats command calculates memory metrics using the following explicit formulas:

Used / Free Memory:


$$\text{Used} = \sum \text{size of allocated blocks}, \quad \text{Free} = \sum \text{size of free holes}$$

Largest Hole:


$$\text{Largest Hole} = \max(\text{size of all free blocks})$$


(Represents the largest single allocation request that can currently succeed; 0 if full).

External Fragmentation:


$$\text{Fragmentation \%} = \left(1 - \frac{\text{Largest Hole}}{\text{Total Free Memory}}\right) \times 100$$

0.0% indicates all free space is consolidated into a single contiguous hole (or 0 bytes remain free).

Values approaching 100% indicate free memory is scattered into small, unusable fragments.
