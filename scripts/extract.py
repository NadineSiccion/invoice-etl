import subprocess

def main():
    print("Running subprocess...")
    try:
        # subprocess.run(r".\scripts\test.bat", shell=True, check=True)
        result = subprocess.run(
            r"wscript.exe .\scripts\run_macro.vbs",
            shell=True, 
            check=True,
            capture_output=True)
        
        print("✅ Successful proccess.")
    except subprocess.CalledProcessError as e:
        print(f'❌ CallProcessError: {e}')
    except subprocess.SubprocessError as e:
        print(f'❌ SubprocessError: {e}')
    except Exception as e:
        print(f"ERROR: {e}")

main()