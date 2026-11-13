import os
import shutil
import sys
import tempfile
import PyInstaller.__main__

work_dir = os.path.join(tempfile.gettempdir(), 'pyi_soccer_build')
dist_dir = os.path.join(tempfile.gettempdir(), 'pyi_soccer_dist')

for d in [work_dir, dist_dir]:
    if os.path.exists(d):
        try:
            shutil.rmtree(d, ignore_errors=True)
        except Exception:
            pass

print(f"Starting PyInstaller build with workpath={work_dir}, distpath={dist_dir}...")
PyInstaller.__main__.run([
    'soccer.spec',
    '--noconfirm',
    f'--workpath={work_dir}',
    f'--distpath={dist_dir}',
])

src_exe = os.path.join(dist_dir, '왕하준의 축구대장.exe')
if not os.path.exists(src_exe):
    print(f"Error: {src_exe} not found!")
    sys.exit(1)

project_root = os.path.dirname(os.path.abspath(__file__))
project_dist = os.path.join(project_root, 'dist')
os.makedirs(project_dist, exist_ok=True)
local_dst = os.path.join(project_dist, '왕하준의 축구대장.exe')
shutil.copy2(src_exe, local_dst)
print(f"Successfully copied to: {local_dst}")

# Check desktops
user_profile = os.environ.get('USERPROFILE', '')
desktops = [
    os.path.join(user_profile, 'OneDrive', 'Desktop'),
    os.path.join(user_profile, 'Desktop'),
    os.path.join(user_profile, 'OneDrive', '바탕 화면'),
    os.path.join(user_profile, '바탕 화면'),
]

copied = 0
for d in dict.fromkeys(desktops):
    if os.path.exists(d):
        try:
            dst = os.path.join(d, '왕하준의 축구대장.exe')
            shutil.copy2(src_exe, dst)
            print(f"Successfully copied to desktop: {dst}")
            copied += 1
        except Exception as e:
            print(f"Warning: Failed to copy to {d}: {e}")

if copied == 0:
    print("Notice: Desktop folder not copied, but exe is ready in dist/")
else:
    print("Build and deployment completed successfully!")


