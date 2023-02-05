import json, shlex, subprocess, logging
from os import path

def upload_to_rclone(local_path, remotes, local_base, state_file, rclone_path, rclone_lock, log_file):
    """
    Uploads the local file to the remote using rclone, rotating the remote each time based on the state stored in the state file.

    :param local_path: The path of the local file to be uploaded
    :param remotes: The list of remotes to rotate
    :param local_base: The base directory of the local files
    :param state_file: The file to store the state in
    :param rclone_path: The path to the rclone executable
    :param rclone_lock: The lock used to synchronize access to the state file
    :param log_file: The file to log the results to
    """
    try:
        # Validate inputs
        if not path.isfile(local_path):
            raise ValueError(f"The local file {local_path} does not exist.")
        if not remotes:
            raise ValueError("The list of remotes cannot be empty.")
        if not path.isdir(local_base):
            raise ValueError(f"The local base directory {local_base} does not exist.")
        if not path.isfile(state_file):
            raise ValueError(f"The state file {state_file} does not exist.")
        if not path.isfile(rclone_path):
            raise ValueError(f"The rclone executable {rclone_path} does not exist.")

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

        command = f"rclone move {local_path} {remote_path} -v --stats=5s --log-file {log_file}"
        result = subprocess.run(command, shell=True, capture_output=True)
        print(result.stdout)
        print(result.stderr)

        # Save the updated state
        state = {"index": index}
        with rclone_lock:
            with open(state_file, "w") as f:
                json.dump(state, f)

    except Exception as e:
        logging.error(f"An error occurred while uploading the file to the remote: {e}")
        raise