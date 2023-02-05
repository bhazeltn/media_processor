import os, subprocess, shlex

def convert(video_file, sickbeard_path, python_path):
    """Convert a video file to an M4V file using the Sickbeard library.

    Arguments:
        video_file (str): The path to the video file to be converted.
        sickbeard_path (str): The path to the Sickbeard MP4 Automator script.
        python_path (str): The path to the Python interpreter.

    Returns:
        str: The path to the converted M4V file, or None if the conversion failed.

    Raises:
        FileNotFoundError: If `video_file` does not exist.
        subprocess.CalledProcessError: If the conversion fails.
    """
    
    print("Converting...")
    if not os.path.isfile(video_file):
        raise FileNotFoundError(f"{video_file} does not exist")
    if not os.path.isfile(sickbeard_path):
        raise FileNotFoundError(f"{sickbeard_path} does not exist")
    if not os.path.isfile(python_path):
        raise FileNotFoundError(f"{python_path} does not exist")

    base, ext = os.path.splitext(video_file)
    new_path = f"{base}.m4v"
    video_file = shlex.quote(video_file)
    command = f"{python_path} {sickbeard_path} -i {video_file} -a"
    print(command)
    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        return None
    return new_path