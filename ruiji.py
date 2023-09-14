import subprocess, os

def img_search(img_name):
    """
    Search for anime images using Ruiji.
    img_name input example: "1.jpg"
    """
    command = f"./ruiji {img_name}"

    try:
        # Start the command as a subprocess
        process = subprocess.Popen(
            command,
            shell=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
        )

        # Communicate with the subprocess
        output, _ = process.communicate(input="-1\n")

        output = output.split("Which one to download?")[0]

        # Print the saved output
        os.remove(img_name)
        return(output)

    except subprocess.CalledProcessError as e:
        # If the command returns a non-zero exit code, handle the error
        os.remove(img_name)
        return(f"Command failed with error: {e}")
    except Exception as e:
        # If there was any other error, handle the error
        os.remove(img_name)
        return(f"Command failed with error: {e}")
    
    # Remove the image from the directory