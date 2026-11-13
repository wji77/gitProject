import os
import shutil
import sys
import tempfile
import PyInstaller.__main__

work_dir = os.path.join(tempfile.gettempdir(), 'pyi_soccer_build')
if os.path.exists(work_dir):
    try:
        shutil.rmtree(work_dir, ignore_errors=True)
    except Exception:
        pass

print(f"Starting PyInstaller build with workpath={work_dir}...")
PyInstaller.__main__.run([
    'soccer.spec',
    '--noconfirm',
    f'--workpath={work_dir}',
])

src_exe = os.path.join('dist', '왕하준의 축구대장.exe')
if not os.path.exists(src_exe):
    print(f"Error: {src_exe} not found!")
    sys.exit(1)

# Check desktops
desktops = [
    os.path.join(os.environ['USERPROFILE'], 'OneDrive', 'Desktop'),
    os.path.join(os.environ['USERPROFILE'], 'Desktop'),
]

copied = 0
for d in desktops:
    if os.path.exists(d):
        dst = os.path.join(d, '왕하준의 축구대장.exe')
        shutil.copy2(src_exe, dst)
        print(f"Successfully copied to: {dst}")
        copied += 1

if copied == 0:
    print("Warning: Desktop folder not found!")
else:
    print("Build and deployment completed successfully!")

