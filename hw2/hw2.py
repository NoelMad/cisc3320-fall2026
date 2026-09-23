# Provides tools to interact with the operating system (files, directories, env variables)
import os

# Helps split and parse Unix shell-like command lines correctly
import shlex

# Controls system-specific parameters and functions (like command-line arguments)
import sys


# Define a function named parse_command_line that takes the raw text entered by the user
def parse_command_line(user_input):
    """Tokenizes input, checks for trailing '&', and identifies built-ins."""

    # --- Step 1: Tokenize Input ---
    # Convert raw input string into a list of individual words (tokens)
    tokens = shlex.split(user_input)

    # Check if the list of words is empty (e.g., if user pressed Enter)
    if not tokens:
        return [], False, False

    # --- Step 2: Strip A Trailing & ---
    # Create variable to track whether this command should run in background
    is_background = False

    # Check if the last token in our list is equal to the string "&"
    if tokens[-1] == "&":
        is_background = True
        tokens.pop()  # Remove trailing '&' so it is not passed to executable

    # Check if list became empty after removing '&' (e.g., user typed only '&')
    if not tokens:
        return [], False, False

    # --- Step 3: Check Against Built-Ins List ---
    # Define list containing all built-in shell commands handled internally
    built_ins = ["cd", "exit", "jobs", "fg", "kill"]

    # Get the first word (command name)
    first_word = tokens[0]

    # Check if command name exists inside built_ins list
    is_builtin = first_word in built_ins

    # Return cleaned command list, background flag, and built-in flag
    return tokens, is_background, is_builtin


def handle_builtin(tokens):
    """Executes built-in shell commands directly within the main process."""
    command = tokens[0]

    # --- 1. HANDLE 'exit' ---
    if command == "exit":
        print("Exiting shell...")
        sys.exit(0)  # Terminate shell program safely

    # --- 2. HANDLE 'cd' ---
    elif command == "cd":
        try:
            # If user typed just 'cd', default to Home directory
            if len(tokens) == 1:
                target_dir = os.environ.get("HOME", "/")
            else:
                target_dir = tokens[1]

            # Change current working directory
            os.chdir(target_dir)
        except FileNotFoundError:
            print(f"cd: no such file or directory: {tokens[1]}")
        except PermissionError:
            print(f"cd: permission denied: {tokens[1]}")
        except Exception as e:
            print(f"cd error: {e}")

    # --- 3. HANDLE 'jobs' ---
    elif command == "jobs":
        print("[Built-in] Listing active background jobs...")

    # --- 4. HANDLE 'fg' ---
    elif command == "fg":
        if len(tokens) < 2:
            print("fg: usage: fg <job_id>")
        else:
            print(f"[Built-in] Moving job {tokens[1]} to foreground...")

    # --- 5. HANDLE 'kill' ---
    elif command == "kill":
        if len(tokens) < 2:
            print("kill: usage: kill <job_id or pid>")
        else:
            print(f"[Built-in] Sending kill signal to process/job {tokens[1]}...")


def main():
    while True:
        try:
            # Display prompt and get raw input
            user_input = input("myshell> ")
        except (EOFError, KeyboardInterrupt):
            # Handle Ctrl+D or Ctrl+C gracefully
            print("\nExiting shell...")
            break

        # Step 1: Parse the line
        tokens, is_background, is_builtin = parse_command_line(user_input)

        # Skip empty lines
        if not tokens:
            continue

        # Step 2: If it is a built-in command, handle it directly!
        if is_builtin:
            handle_builtin(tokens)
        else:
            # Step 3 (Upcoming): External commands will go here
            print(
                f"[External Command Placeholder] Executing: {tokens} (Background: {is_background})"
            )


if __name__ == "__main__":
    main()
