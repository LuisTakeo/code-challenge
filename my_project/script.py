import subprocess

def run_meltano_elt():
    try:
        # Execute o comando Meltano ELT
        result = subprocess.run(
            ["meltano", "elt", "tap-postgres", "target-csv"],
            check=True,
            capture_output=True,
            text=True
        )
        print("Meltano ELT output:", result.stdout)
    except subprocess.CalledProcessError as e:
        print("Error running Meltano ELT:", e.stderr)

if __name__ == "__main__":
    run_meltano_elt()