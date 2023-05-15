import subprocess

try:
    # Execute the lsof command and get the output
    output = subprocess.check_output(["sudo", "lsof", "/dev/video0"]).decode()
except subprocess.CalledProcessError:
    print("No process is currently accessing /dev/video0.")
else:
    # Find the PID of the process that is using the camera
    lines = output.strip().split('\n')
    if len(lines) > 1: # the first line is the header, so we start from the second line
        fields = lines[1].split()
        pid = fields[1] # PID is the second field

        # Kill the process
        subprocess.run(["sudo", "kill", "-9", pid])

        print(f"Killed process {pid} that was using /dev/video0.")