import streamlit as st
import subprocess, os

st.set_page_config(page_title="AI-assisted Symbolic Execution Demo")
st.title("AI-assisted Symbolic Execution Demo")

st.markdown("""
Upload a small C program. The app will:
1. compile it,
2. run symbolic execution (mocked on Cloud),
3. apply a template patch and show the fixed code.
""")

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # folder of app.py
SRC_DIR = os.path.join(BASE_DIR, "..", "src")          # path to src folder
FIND_BUG_MOCK = os.path.join(SRC_DIR, "find_bug_mock.py")
AUTO_PATCH = os.path.join(SRC_DIR, "auto_patch.py")

uploaded = st.file_uploader("Upload C file (small)", type=["c"])
if not uploaded:
    st.info("Upload a C file (use the provided `bugprog.c` for demo).")
else:
    src_path = os.path.join(BASE_DIR, "bugprog.c")
    with open(src_path, "wb") as f:
        f.write(uploaded.read())

    st.subheader("Uploaded source")
    st.code(open(src_path).read(), language="c")

    # Compile
    st.subheader("Compiling program")
    compile_proc = subprocess.run(["gcc", "-o", "bugprog", src_path], capture_output=True, text=True)
    if compile_proc.returncode != 0:
        st.error("Compilation failed:\n" + compile_proc.stderr)
    else:
        st.success("Compilation succeeded.")

        # Run symbolic execution mock
        st.subheader("Running symbolic execution (mock)")
        if os.path.exists(FIND_BUG_MOCK):
            mock = subprocess.run(["python3", FIND_BUG_MOCK], capture_output=True, text=True)
            st.text("Mock finder output:\n" + mock.stdout)
        else:
            st.error(f"Mock finder script not found at {FIND_BUG_MOCK}")

        # Apply template patch
        st.subheader("Applying automatic template patch")
        fixed_path = os.path.join(BASE_DIR, "bugprog_fixed.c")
        if os.path.exists(AUTO_PATCH):
            patch_proc = subprocess.run(["python3", AUTO_PATCH, src_path, fixed_path],
                                        capture_output=True, text=True)
            st.text(patch_proc.stdout + patch_proc.stderr)

            if os.path.exists(fixed_path):
                st.success("Patch applied. Fixed code:")
                st.code(open(fixed_path).read(), language="c")

                # Compile fixed program
                st.subheader("Compile and run fixed program with input '0'")
                comp2 = subprocess.run(["gcc", "-o", "bugprog_fixed", fixed_path],
                                       capture_output=True, text=True)
                if comp2.returncode == 0:
                    run = subprocess.run(["./bugprog_fixed", "0"], capture_output=True, text=True)
                    st.text("Program output:\n" + run.stdout + run.stderr)
                else:
                    st.error("Failed to compile fixed program:\n" + comp2.stderr)
            else:
                st.error("Patch did not generate bugprog_fixed.c")
        else:
            st.error(f"Auto patch script not found at {AUTO_PATCH}")
