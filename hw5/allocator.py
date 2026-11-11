import sys

class ToyHeapAllocator:
    def __init__(self, total_size=1000, policy="first-fit"):
        self.total_size = total_size
        self.policy = policy.lower()
        
        if self.policy not in ["first-fit", "best-fit", "worst-fit"]:
            print(f"Warning: Unknown policy '{policy}'. Defaulting to 'first-fit'.")
            self.policy = "first-fit"
            
        # Initial state: One giant free block spanning the whole pool
        self.blocks = [
            {"offset": 0, "size": total_size, "is_allocated": False, "name": None}
        ]

    def set_policy(self, new_policy):
        new_policy = new_policy.lower()
        if new_policy in ["first-fit", "best-fit", "worst-fit"]:
            self.policy = new_policy
            print(f"Policy successfully updated to: {self.policy.upper()}")
        else:
            print(f"Error: Unknown policy '{new_policy}'. Use first-fit, best-fit, or worst-fit.")

    def alloc(self, name, size):
        # STAGE 2: Validate
        if size <= 0:
            print("Error: Allocation size must be greater than 0.")
            return None

        for block in self.blocks:
            if block["is_allocated"] and block["name"] == name:
                print(f"Error: Allocation name '{name}' already exists.")
                return None

        # STAGE 3: Search the free list
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
                        if diff < best_size_diff:
                            best_size_diff = diff
                            target_block = block

        elif self.policy == "worst-fit":
            max_size = -1
            for block in self.blocks:
                if not block["is_allocated"] and block["size"] >= size:
                    if block["offset"] + size <= self.total_size:
                        if block["size"] > max_size:
                            max_size = block["size"]
                            target_block = block

        if target_block is None:
            print(f"Error: Out of memory. No free block large enough to satisfy {size} bytes.")
            return None

        # STAGE 4: Update the structures (Splitting)
        remaining_size = target_block["size"] - size
        target_block["size"] = size
        target_block["is_allocated"] = True
        target_block["name"] = name
        
        if remaining_size > 0:
            new_block = {
                "offset": target_block["offset"] + size,
                "size": remaining_size,
                "is_allocated": False,
                "name": None
            }
            idx = self.blocks.index(target_block)
            self.blocks.insert(idx + 1, new_block)
        
        # STAGE 5: Report
        print(f"Successfully allocated {size} bytes for '{name}' at address offset {target_block['offset']}")
        return target_block["offset"]

    def free(self, name):
        # STAGE 2: Validate existence
        target_block = None
        for block in self.blocks:
            if block["is_allocated"] and block["name"] == name:
                target_block = block
                break

        if target_block is None:
            print(f"Error: Unknown name '{name}'. No active allocation found with this name.")
            return False

        if not target_block["is_allocated"]:
            print(f"Error: Double free detected for allocation '{name}'.")
            return False

        # STAGE 4: Update the structures & Coalesce
        target_block["is_allocated"] = False
        target_block["name"] = None
        self._coalesce()
        
        # STAGE 5: Report
        print(f"Successfully freed allocation '{name}' and coalesced adjacent free blocks.")
        return True

    def _coalesce(self):
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

        for b in self.blocks:
            if b["is_allocated"]:
                used_bytes += b["size"]
            else:
                free_bytes += b["size"]
                number_of_holes += 1
                if b["size"] > largest_hole:
                    largest_hole = b["size"]

        if free_bytes == 0 or number_of_holes <= 1:
            fragmentation_pct = 0.0
        else:
            fragmentation_pct = (1.0 - (largest_hole / free_bytes)) * 100.0

        print("\n=== PyShell OS Heap Statistics ===")
        print(f"Policy:                  {self.policy.upper()}")
        print(f"Total Pool Size:         {self.total_size} bytes")
        print(f"Used Memory:             {used_bytes} bytes")
        print(f"Free Memory:             {free_bytes} bytes")
        print(f"Largest Hole:            {largest_hole} bytes")
        print(f"Number of Holes (Free):  {number_of_holes}")
        print(f"External Fragmentation:  {fragmentation_pct:.2f}%")
        print("==================================\n")

    def map_heap(self):
        print(f"\n=== PyShell OS Heap Map (Policy: {self.policy.upper()}) ===")
        print(f"{'Index':<6} | {'Range':<15} | {'Size':<6} | {'Status':<12} | {'Name':<10}")
        print("-" * 60)
        for i, b in enumerate(self.blocks):
            end_addr = b['offset'] + b['size'] - 1
            addr_range = f"{b['offset']} - {end_addr}"
            status = "ALLOCATED" if b["is_allocated"] else "FREE"
            name_str = b['name'] if b['name'] else "-"
            print(f"{i:<6} | {addr_range:<15} | {b['size']:<6} | {status:<12} | {name_str:<10}")
        print("============================================================\n")


def main():
    pool_size = 1000
    policy = "first-fit"

    if len(sys.argv) > 1:
        try:
            pool_size = int(sys.argv[1])
        except ValueError:
            policy = sys.argv[1]

    if len(sys.argv) > 2:
        policy = sys.argv[2]

    heap = ToyHeapAllocator(pool_size, policy)
    print(f"PyShell OS Heap Allocator Initialized")
    print(f"Pool Size: {pool_size} bytes | Policy: {policy.upper()}")
    print("\nAvailable Commands:")
    print("  alloc <name> <size>    - Allocate a named block")
    print("  free <name>            - Free a block by name")
    print("  policy <first|best|w>  - Change placement policy on the fly")
    print("  stats                  - View memory metrics & fragmentation")
    print("  map                    - Print block layout map")
    print("  exit                   - Exit the shell\n")

    while True:
        try:
            # STAGE 1: Read a command
            user_input = input("pyshell-heap> ").strip().split()
            if not user_input:
                continue
            
            cmd = user_input[0].lower()
            
            if cmd == "exit":
                print("Exiting heap shell...")
                break
            elif cmd == "map":
                heap.map_heap()
            elif cmd == "stats":
                heap.stats()
            elif cmd == "policy":
                if len(user_input) < 2:
                    print("Usage: policy <first-fit|best-fit|worst-fit>")
                    continue
                heap.set_policy(user_input[1])
            elif cmd == "alloc":
                if len(user_input) < 3:
                    print("Usage: alloc <name> <size>")
                    continue
                name = user_input[1]
                try:
                    size = int(user_input[2])
                    heap.alloc(name, size)
                except ValueError:
                    print("Error: Size must be a valid integer.")
            elif cmd == "free":
                if len(user_input) < 2:
                    print("Usage: free <name>")
                    continue
                name = user_input[1]
                heap.free(name)
            else:
                print(f"Unknown command: '{cmd}'. Try alloc, free, policy, stats, map, or exit.")
        except KeyboardInterrupt:
            print("\nExiting...")
            break

if __name__ == "__main__":
    main()
