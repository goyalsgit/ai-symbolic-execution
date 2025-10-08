# app.py - Streamlit front-end for the demo
import streamlit as st
import subprocess, os

st.set_page_config(page_title="AI-assisted Symbolic Execution Demo")
st.title("AI-assisted Symbolic Execution Demo")

st.markdown("""
Upload a small C program. The app will:
1. compile it,
2. try to run symbolic execution (angr) to find a crashing input,
3. apply a template patch and show the fixed code.
(If angr can't be installed on the server, a lightweight mock will be used.)
""")

uploaded = st.file_uploader("Upload C file (small)", type=["c"])
if not uploaded:
    st.info("Upload a C file (use the provided `bugprog.c` for demo).")
else:
    # save uploaded file
    src_path = "bugprog.c"
    with open(src_path, "wb") as f:
        f.write(uploaded.read())
    st.subheader("Uploaded source")
    st.code(open(src_path).read(), language="c")

    # compile
    st.subheader("Compiling program")
    compile_proc = subprocess.run(["gcc", "-o", "bugprog", src_path], capture_output=True, text=True)
    if compile_proc.returncode != 0:
        st.error("Compilation failed:\n" + compile_proc.stderr)
    else:
        st.success("Compilation succeeded.")

        # try to run the real finder; fallback to mock
        st.subheader("Running symbolic execution (may be slow / not supported on Cloud)")
        try:
            import importlib
            angr_spec = importlib.util.find_spec("angr")
            if angr_spec is None:
                raise ImportError("angr not found")
            res = subprocess.run(["python3", "find_bug.py"], capture_output=True, text=True, timeout=120)
            st.text("Real finder output:\n" + res.stdout + res.stderr)
        except Exception as e:
            st.warning(f"Could not run angr solver here: {e}\nUsing mock output for demo.")
            mock = subprocess.run(["python3", "find_bug_mock.py"], capture_output=True, text=True)
            st.text("Mock finder output:\n" + mock.stdout)

        # apply template patch
        st.subheader("Applying automatic template patch")
        patch_proc = subprocess.run(["python3", "auto_patch.py", src_path, "bugprog_fixed.c"], capture_output=True, text=True)
        st.text(patch_proc.stdout + patch_proc.stderr)
        if os.path.exists("bugprog_fixed.c"):
            st.success("Patch applied. Fixed code:")
            st.code(open("bugprog_fixed.c").read(), language="c")

            # compile fixed and run with input 0
            st.subheader("Compile and run fixed program with input '0'")
            comp2 = subprocess.run(["gcc", "-o", "bugprog_fixed", "bugprog_fixed.c"], capture_output=True, text=True)
            if comp2.returncode == 0:
                run = subprocess.run(["./bugprog_fixed", "0"], capture_output=True, text=True)
                st.text("Program output:\n" + run.stdout + run.stderr)
            else:
                st.error("Failed to compile fixed program:\n" + comp2.stderr)
