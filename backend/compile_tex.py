# backend/compile_tex.py

import os
import subprocess

def is_cloud_environment():
    return os.environ.get("STREAMLIT_SERVER_HEADLESS") == "1"

def compile_tex_to_pdf(tex_path: str, output_dir: str = "output/cover_letters/"):
    """
    Compile a LaTeX file to PDF using pdflatex inside a Docker container.
    Requires Docker and the texlive-full image.
    Note: Streamlit Cloud uses a headless environment, so compilation is skipped.
    """
    if is_cloud_environment():
        print("⚠️ PDF compilation skipped on Streamlit Cloud.")
        return

    abs_tex_path = os.path.abspath(tex_path)
    abs_output_dir = os.path.abspath(output_dir)
    tex_filename = os.path.basename(tex_path)

    cmd = [
        "docker", "run", "--rm",
        "-v", f"{abs_output_dir}:/data",
        "-w", "/data",
        "ghcr.io/xu-cheng/texlive-full:latest",
        "pdflatex", tex_filename
    ]

    print(f"🛠️ Compiling {tex_filename} via Docker...")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print("❌ PDF compilation failed:")
        print(result.stdout)
        print(result.stderr)
    else:
        print(f"✅ PDF generated in: {abs_output_dir}")