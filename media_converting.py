import os, subprocess, shlex

def convert(video_file, sickbeard, python):
  base, ext = os.path.splitext(video_file)
  new_path = f"{base}.m4v"
  video_file = shlex.quote(video_file)
  subprocess.run(f"{python} {sickbeard} -i {video_file} -a", shell=True)
  return new_path

