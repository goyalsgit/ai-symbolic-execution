import streamlit as st
import sqlite3
import os
import subprocess

# ------------------ DATABASE SETUP ------------------
def init_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT
    )''')
    conn.commit()
    conn.close()

def add_user(username, password):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
    except sqlite3.IntegrityError:
        return False  # username already exists
    finally:
        conn.close()
    return True

def check_user(username, password):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    result = c.fetchone()
    conn.close()
    return result is not None


# ------------------ LOGIN & SIGNUP PAGES ------------------
def login_page():
    st.title("🔐 Login Page")
    st.write("Please log in to access the AI-assisted Symbolic Execution tool.")

    user = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if check_user(user, password):
            st.session_state["user"] = user
            st.success(f"✅ Welcome {user}!")
            st.session_state["page"] = "app"
            st.rerun()
        else:
            st.error("Invalid username or password")

    st.info("Don’t have an account?")
    if st.button("Go to Signup"):
        st.session_state["page"] = "signup"
        st.rerun()


def signup_page():
    st.title("📝 Signup Page")
    st.write("Create a new account to use the app.")

    user = st.text_input("Choose a username")
    password = st.text_input("Choose a password", type="password")

    if st.button("Signup"):
        if add_user(user, password):
            st.success("✅ Account created successfully! Please log in.")
            st.session_state["page"] = "login"
            st.rerun()
        else:
            st.error("⚠️ Username already exists! Try another one.")

    st.info("Already have an account?")
    if st.button("Go to Login"):
        st.session_state["page"] = "login"
        st.rerun()


# ------------------ MAIN APP ------------------
def symbolic_execution_app():
    st.set_page_config(page_title="AI-assisted Symbolic Execution Demo")
    st.title("🤖 AI-assisted Symbolic Execution Demo")

    st.markdown("""
    Upload a small C program. The app will:
    1. Compile it
    2. Run symbolic execution (mocked)
    3. Apply a template patch and show the fixed code.
    """)

    # Logout button
    if st.button("Logout"):
        st.session_state.pop("user", None)
        st.session_state["page"] = "login"
        st.rerun()

    # Get reliable paths for all environments
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    SRC_DIR = os.path.join(BASE_DIR, "src")

    # In case Streamlit runs from a different working directory
    if not os.path.exists(SRC_DIR):
        SRC_DIR = os.path.join(os.path.dirname(BASE_DIR), "src")

    FIND_BUG_MOCK = os.path.join(SRC_DIR, "find_bug_mock.py")
    AUTO_PATCH = os.path.join(SRC_DIR, "auto_patch.py")

    # Debug info (remove later if not needed)
    st.caption(f"📂 Searching mock script at: {FIND_BUG_MOCK}")

    # File uploader
    uploaded = st.file_uploader("Upload C file (small)", type=["c"])
    if not uploaded:
        st.info("Upload a C file (use the provided `bugprog.c` for demo).")
        return

    src_path = os.path.join(BASE_DIR, "bugprog.c")
    with open(src_path, "wb") as f:
        f.write(uploaded.read())

    st.subheader("Uploaded Source")
    st.code(open(src_path).read(), language="c")

    # Compile uploaded C file
    st.subheader("🔧 Compiling Program")
    compile_proc = subprocess.run(["gcc", "-o", "bugprog", src_path],
                                  capture_output=True, text=True)
    if compile_proc.returncode != 0:
        st.error("❌ Compilation failed:\n" + compile_proc.stderr)
        return
    else:
        st.success("✅ Compilation succeeded.")

    # Run symbolic execution mock
    st.subheader("🧠 Running Symbolic Execution (Mock)")
    if os.path.exists(FIND_BUG_MOCK):
        mock = subprocess.run(["python3", FIND_BUG_MOCK],
                              capture_output=True, text=True)
        st.text("Mock Finder Output:\n" + mock.stdout)
    else:
        st.error(f"⚠️ Mock finder script not found at {FIND_BUG_MOCK}")
        return

    # Apply template patch
    st.subheader("🩹 Applying Automatic Template Patch")
    fixed_path = os.path.join(BASE_DIR, "bugprog_fixed.c")
    if os.path.exists(AUTO_PATCH):
        patch_proc = subprocess.run(["python3", AUTO_PATCH, src_path, fixed_path],
                                    capture_output=True, text=True)
        st.text(patch_proc.stdout + patch_proc.stderr)

        if os.path.exists(fixed_path):
            st.success("✅ Patch applied. Fixed code:")
            st.code(open(fixed_path).read(), language="c")

            # Compile and run fixed program
            st.subheader("🚀 Compile and Run Fixed Program (input '0')")
            comp2 = subprocess.run(["gcc", "-o", "bugprog_fixed", fixed_path],
                                   capture_output=True, text=True)
            if comp2.returncode == 0:
                run = subprocess.run(["./bugprog_fixed", "0"],
                                     capture_output=True, text=True)
                st.text("Program Output:\n" + run.stdout + run.stderr)
            else:
                st.error("❌ Failed to compile fixed program:\n" + comp2.stderr)
        else:
            st.error("❌ Patch did not generate bugprog_fixed.c")
    else:
        st.error(f"⚠️ Auto patch script not found at {AUTO_PATCH}")


# ------------------ MAIN CONTROL FLOW ------------------
if "page" not in st.session_state:
    st.session_state["page"] = "login"

if "user" in st.session_state:
    symbolic_execution_app()
elif st.session_state["page"] == "login":
    init_db()
    login_page()
elif st.session_state["page"] == "signup":
    init_db()
    signup_page()
