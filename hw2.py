import os
import shlex
import signal
import sys

# --- THE JOB DATA STRUCTURE ---
class Job:
    def __init__(self, pid, command, background):
        self.pid = pid
        self.command = command
        self.background = background
        self.status = "Running"  # Running, Stopped, Done

def reap_zombies(jobs):
    """
    Reaps terminated child processes without blocking and updates 
    their status to 'Done' in the jobs dictionary for the jobs built-in.
    """
    while True:
        try:
            pid, status = os.waitpid(-1, os.WNOHANG)
            if pid == 0:
                break
            
            # Find the tracked job and change its status to Done instead of printing/deleting
            for job_id, job_obj in jobs.items():
                if job_obj.pid == pid:
                    job_obj.status = "Done"
                    break

        except ChildProcessError:
            break
        except OSError:
            break


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
    """Executes built-in shell commands using the Job class objects."""
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

    # 3. jobs
    elif command == "jobs":
        if not jobs:
            print("No active background jobs.")
        else:
            for job_id, job_obj in jobs.items():
                print(f"[{job_id}]  {job_obj.status}         {job_obj.command}")

    # 4. fg
    elif command == "fg":
        if len(tokens) < 2:
            print("fg: usage: fg <job_id>")
            return

        target = tokens[1]
        if target.startswith("%"):
            target = target[1:]

        if not target.isdigit():
            print(f"fg: invalid job id: {tokens[1]}")
            return

        job_id = int(target)
        if job_id not in jobs:
            print(f"fg: job not found: {job_id}")
            return

        job_obj = jobs[job_id]
        pid = job_obj.pid
        print(f"{job_obj.command}")

        try:
            os.kill(pid, signal.SIGCONT)
        except ProcessLookupError:
            pass

        # Remove from dictionary since it's back in the foreground
        del jobs[job_id]
        
        try:
            os.waitpid(pid, 0)
        except ChildProcessError:
            print(f"fg: no child process with PID {pid}")
        except Exception as e:
            print(f"fg error: {e}")

    # 5. kill
    elif command == "kill":
        if len(tokens) < 2:
            print("kill: usage: kill <job_id or pid>")
            return

        target = tokens[1]
        if target.startswith("%"):
            target = target[1:]

        target_pid = None
        matched_job_id = None

        if target.isdigit():
            val = int(target)
            if val in jobs:
                matched_job_id = val
                target_pid = jobs[val].pid
            else:
                target_pid = val

        if target_pid:
            try:
                os.kill(target_pid, signal.SIGTERM)
                if matched_job_id is not None:
                    print(f"[{matched_job_id}] Terminated {jobs[matched_job_id].command}")
                    del jobs[matched_job_id]
                else:
                    print(f"[{target_pid}] Terminated")
            except ProcessLookupError:
                print(f"kill: ({target_pid}) - No such process")
            except Exception as e:
                print(f"kill error: {e}")

def run_external_command(tokens, is_background, jobs, next_job_id):
    """Forks a process and saves a Job object into the jobs dictionary."""
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
                cmd_str = " ".join(tokens)
                jobs[next_job_id] = Job(pid, cmd_str, background=True)
                # Match the slide format: [job_id] pid command
                print(f"[{next_job_id}] {pid} {cmd_str}")
                next_job_id += 1
        else:
            print("myshell: failed to fork process")

    except OSError as e:
        print(f"myshell: fork failed: {e}")

    return next_job_id


def main():
    jobs = {}  # job_id -> Job object
    next_job_id = 1  

    while True:
        reap_zombies(jobs)

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
