import sys

class ToyHeapAllocator:
    def __init__(self, total_size=1000, policy=None):
        self.total_size = total_size
        self.policy = "first-fit"
        if policy:
            self.set_policy(policy)
        
        # Initial state: One giant free block spanning the whole pool
        self.blocks = [
            {"offset": 0, "size": total_size, "is_allocated": False, "name": None}
        ]
        self._check_invariants()

    def set_policy(self, new_policy):
        new_policy = new_policy.lower()
        if new_policy in ["first", "first-fit"]:
            self.policy = "first-fit"
            return True, "policy: first-fit"
        elif new_policy in ["best", "best-fit"]:
            self.policy = "best-fit"
            return True, "policy: best-fit"
        elif new_policy in ["worst", "worst-fit"]:
            self.policy = "worst-fit"
            return True, "policy: worst-fit"
        else:
            return False, f"Error: Unknown policy '{new_policy}'."

    def _check_invariants(self):
        """Invariant check: ensures used + free == total_size and no gaps/overlaps[cite: 4]."""
        total_allocated = sum(b["size"] for b in self.blocks if b["is_allocated"])
        total_free = sum(b["size"] for b in self.blocks if not b["is_allocated"])
        
        assert total_allocated + total_free == self.total_size, \
            f"Invariant Error: Used ({total_allocated}) + Free ({total_free}) != Total Size ({self.total_size})"
        
        expected_offset = 0
        for b in self.blocks:
            assert b["offset"] == expected_offset, \
                f"Invariant Error: Block offset {b['offset']} does not match expected {expected_offset}"
            assert b["size"] > 0, f"Invariant Error: Block size must be greater than 0, got {b['size']}"
            expected_offset += b["size"]
            
        assert expected_offset == self.total_size, \
            f"Invariant Error: Total block span {expected_offset} != Pool Size {self.total_size}"

    def alloc(self, name, size):
        """Returns (success_bool, result_message_or_offset). Pure function for PyShell integration[cite: 6, 7]."""
        if size <= 0:
            return False, "Error: Allocation size must be greater than 0."

        for block in self.blocks:
            if block["is_allocated"] and block["name"] == name:
                return False, f"Error: Allocation name '{name}' already exists."

        target_block = None

        if self.policy == "first-fit":
            for block in self.blocks:
                if not block["is_allocated"] and block["size"] >= size:
                    if block["offset"] + size <= self.total_size:
                        target_block = block
                        break

        elif self.policy == "best-fit":
            best_size_diff = float('inf')
            for block in self.blocks:
                if not block["is_allocated"] and block["size"] >= size:
                    if block["offset"] + size <= self.total_size:
                        diff = block["size"] - size
                        # Tie-break: lowest address wins
                        if diff < best_size_diff or (diff == best_size_diff and target_block and block["offset"] < target_block["offset"]):
                            best_size_diff = diff
                            target_block = block

        elif self.policy == "worst-fit":
            max_size = -1
            for block in self.blocks:
                if not block["is_allocated"] and block["size"] >= size:
                    if block["offset"] + size <= self.total_size:
                        # Tie-break: lowest address wins for equal worst-fit size
                        if block["size"] > max_size or (block["size"] == max_size and target_block and block["offset"] < target_block["offset"]):
                            max_size = block["size"]
                            target_block = block

        if target_block is None:
            return False, f"Error: Out of memory. No free block large enough to satisfy {size} bytes."

        start_offset = target_block["offset"]
        remaining_size = target_block["size"] - size
        target_block["size"] = size
        target_block["is_allocated"] = True
        target_block["name"] = name
        
        # Pitfall check: Prevent zero-size holes[cite: 7]
        if remaining_size > 0:
            new_block = {
                "offset": start_offset + size,
                "size": remaining_size,
                "is_allocated": False,
                "name": None
            }
            idx = self.blocks.index(target_block)
            self.blocks.insert(idx + 1, new_block)
        
        # Run invariant check
        self._check_invariants()
        
        end_offset = start_offset + size
        return True, f"{name}: {size} bytes at [{start_offset}-{end_offset}]"

    def free(self, name):
        """Returns (success_bool, result_message). Pure function for PyShell integration[cite: 6, 7]."""
        target_block = None
        for block in self.blocks:
            if block["is_allocated"] and block["name"] == name:
                target_block = block
                break

        if target_block is None:
            return False, f"Error: Unknown name '{name}'."

        if not target_block["is_allocated"]:
            return False, f"Error: Double free detected for allocation '{name}'."

        freed_offset = target_block["offset"]
        freed_size = target_block["size"]
        end_offset = freed_offset + freed_size

        target_block["is_allocated"] = False
        target_block["name"] = None
        
        # Coalesce adjacent free blocks safely
        self._coalesce()
        
        # Run invariant check
        self._check_invariants()
        
        return True, f"{name} freed (hole [{freed_offset}-{end_offset}] {freed_size} bytes)"

    def _coalesce(self):
        """Safely merges adjacent unallocated blocks to prevent slivers[cite: 7]."""
        i = 0
        while i < len(self.blocks) - 1:
            current = self.blocks[i]
            nxt = self.blocks[i + 1]
            
            if not current["is_allocated"] and not nxt["is_allocated"]:
                current["size"] += nxt["size"]
                self.blocks.pop(i + 1)
            else:
                i += 1

    def stats(self):
        used_bytes = 0
        free_bytes = 0
        largest_hole = 0
        number_of_holes = 0
        free_list_strs = []

        for b in self.blocks:
            end_addr = b['offset'] + b['size']
            if b["is_allocated"]:
                used_bytes += b["size"]
            else:
                free_bytes += b["size"]
                number_of_holes += 1
                if b["size"] > largest_hole:
                    largest_hole = b["size"]
                free_list_strs.append(f"[{b['offset']}-{end_addr}]")

        if free_bytes == 0 or number_of_holes <= 1:
            fragmentation_pct = 0.0
        else:
            fragmentation_pct = (1.0 - (largest_hole / free_bytes)) * 100.0

        output = []
        output.append(f"pool {self.total_size}  used {used_bytes}  free {free_bytes}  holes {number_of_holes}")
        output.append(f"largest hole {largest_hole}  fragmentation {fragmentation_pct:.1f}%")
        output.append(f"free list: {' '.join(free_list_strs)}")
        return "\n".join(output)

    def map_heap(self):
        output = [f"\n=== Heap Map (Policy: {self.policy}) ==="]
        for i, b in enumerate(self.blocks):
            end_addr = b['offset'] + b['size']
            status = f"ALLOCATED ({b['name']})" if b["is_allocated"] else "FREE"
            output.append(f"[{b['offset']} - {end_addr}] : {status} (Size: {b['size']})")
        output.append("=========================================\n")
        return "\n".join(output)

    def visualize(self):
        scale = 10
        bar = []
        for b in self.blocks:
            char = b['name'][0].upper() if b["is_allocated"] and b['name'] else '.'
            num_chars = max(1, b['size'] // scale)
            bar.append(char * num_chars)
        return f"[{''.join(bar)}] (1 char = {scale} bytes)"


def main():
    pool_size = 1000
    policy = None

    if len(sys.argv) > 1:
        try:
            pool_size = int(sys.argv[1])
        except ValueError:
            policy = sys.argv[1]

    if len(sys.argv) > 2:
        policy = sys.argv[2]

    heap = ToyHeapAllocator(pool_size, policy)

    while True:
        try:
            user_input = input("alloc> ").strip().split()
            if not user_input:
                continue
            
            cmd = user_input[0].lower()
            
            if cmd == "exit":
                break
            elif cmd == "map":
                print(heap.map_heap())
            elif cmd == "stats":
                print(heap.stats())
            elif cmd in ["visual", "viz"]:
                print(heap.visualize())
            elif cmd == "policy":
                if len(user_input) < 2:
                    print("Usage: policy <first|best|worst>")
                    continue
                success, msg = heap.set_policy(user_input[1])
                print(msg)
            elif cmd == "alloc":
                if len(user_input) < 3:
                    print("Usage: alloc <name> <size>")
                    continue
                name = user_input[1]
                try:
                    size = int(user_input[2])
                    success, msg = heap.alloc(name, size)
                    print(msg)
                except ValueError:
                    print("Error: Size must be an integer.")
            elif cmd == "free":
                if len(user_input) < 2:
                    print("Usage: free <name>")
                    continue
                name = user_input[1]
                success, msg = heap.free(name)
                print(msg)
            else:
                print(f"Unknown command: '{cmd}'")
        except KeyboardInterrupt:
            print()
            break

if __name__ == "__main__":
    main()
