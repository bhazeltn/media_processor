import json, shlex, subprocess
from os import path

def upload_to_rclone(local_path, remotes, local_base, state_file, rclone_path, rclone_lock):
  # Load the state file
  with rclone_lock:
    with open(state_file, "r") as f:
      state = json.load(f)
    index = state["index"]

  # Choose the next remote in the list
  remote = remotes[index]
  index = (index + 1) % len(remotes)  # Increment the index and wrap around if needed

  # Split the local path into its components and remove the part that corresponds to the local base directory
  remote_path = path.relpath(path.dirname(local_path), local_base)
  
  local_path = shlex.quote(local_path)
  remote_path = path.join(remote, remote_path)
  remote_path = shlex.quote(remote_path)

  # Upload the file to the remote
  #subprocess.run([{rclone_path}, "move", local_path, f"{remote}:{remote_path}"])

  # Save the updated state
  state = {"index": index}
  with rclone_lock:
    with open(state_file, "w") as f:
      json.dump(state, f)