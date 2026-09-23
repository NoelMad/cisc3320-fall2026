import os
import shlex
import signal
import sys


def parse_command_line(user_input):
    """Tokenizes input, checks for trailing '&', and identifies built-ins."""
    tokens = shlex.split(user_input)

    if not tokens:
        return [], False, False

    is_background = False
    if tokens[-1] == "&":
        is_background = True
        tokens.pop()

    if not tokens:
        return [], False, False

    built_ins = ["cd", "exit", "jobs", "fg", "kill"]
    is_builtin = tokens[0] in built_ins

    return tokens, is_background, is_builtin


def handle_builtin(tokens, jobs):
    """Executes built-in shell commands using the active jobs collection."""
    command = tokens[0]

    # 1. exit
    if command == "exit":
        print("Exiting shell...")
        sys.exit(0)

    # 2. cd
    elif command == "cd":
        try:
            target_dir = (
                tokens[1] if len(tokens) > 1 else os.environ.get("HOME", "/")
            )
            os.chdir(target_dir)
        except FileNotFoundError:
            print(f"cd: no such file or directory: {tokens[1]}")
        except Exception as e:
            print(f"cd error: {e}")

    # 3. jobs (displays tracked background jobs)
    elif command == "jobs":
        if not jobs:
            print("No active background jobs.")
        else:
            for job_id, info in jobs.items():
                print(
                    f"[{job_id}]  {info['status']}          {info['command']}"
                )

    # 4. fg (placeholder to be completed in Step 5)
    elif command == "fg":
        if len(tokens) < 2:
            print("fg: usage: fg <job_id>")
        else:
            print(f"[Built-in] Moving job {tokens[1]} to foreground...")

    # 5. kill (sends SIGTERM to a job or PID)
    elif command == "kill":
        if len(tokens) < 2:
            print("kill: usage: kill <job_id or pid>")
            return

        target = tokens[1]
        if target.startswith("%"):
            target = target[1:]

        target_pid = None
        if target.isdigit():
            job_id = int(target)
            if job_id in jobs:
                target_pid = jobs[job_id]["pid"]
            else:
                target_pid = job_id

        if target_pid:
            try:
                os.kill(target_pid, signal.SIGTERM)
                print(f"Sent kill signal to PID {target_pid}")
            except ProcessLookupError:
                print(f"kill: ({target_pid}) - No such process")
            except Exception as e:
                print(f"kill error: {e}")


def run_external_command(tokens, is_background, jobs, next_job_id):
    """Forks a process and adds background jobs to the jobs dict."""
    try:
        pid = os.fork()

        if pid == 0:
            # Child process
            try:
                os.execvp(tokens[0], tokens)
            except FileNotFoundError:
                print(f"myshell: command not found: {tokens[0]}")
                sys.exit(1)
            except Exception as e:
                print(f"myshell: execution error: {e}")
                sys.exit(1)

        elif pid > 0:
            # Parent process
            if not is_background:
                os.waitpid(pid, 0)
            else:
                # Save job info in the collection
                cmd_str = " ".join(tokens)
                jobs[next_job_id] = {
                    "pid": pid,
                    "command": cmd_str,
                    "status": "Running",
                }
                print(f"[{next_job_id}] {pid}")
                next_job_id += 1

        else:
            print("myshell: failed to fork process")

    except OSError as e:
        print(f"myshell: fork failed: {e}")

    return next_job_id


def main():
    # Dictionary to store active background jobs
    jobs = {}
    next_job_id = 1

    while True:
        try:
            user_input = input("myshell> ")
        except (EOFError, KeyboardInterrupt):
            print("\nExiting shell...")
            break

        tokens, is_background, is_builtin = parse_command_line(user_input)

        if not tokens:
            continue

        if is_builtin:
            handle_builtin(tokens, jobs)
        else:
            next_job_id = run_external_command(
                tokens, is_background, jobs, next_job_id
            )


if __name__ == "__main__":
    main()
