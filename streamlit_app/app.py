import streamlit as st
import subprocess, os, sqlite3, hashlib

# --------------------------
# Helper Functions
# --------------------------
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    return make_hashes(password) == hashed_text

# --------------------------
# Database Setup
# --------------------------
def create_usertable():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users(username TEXT, password TEXT)')
    conn.commit()
    conn.close()

def add_userdata(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('INSERT INTO users(username,password) VALUES (?,?)', (username, password))
    conn.commit()
    conn.close()

def login_user(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username=? AND password=?', (username, password))
    data = c.fetchall()
    conn.close()
    return data

# --------------------------
# Streamlit Config
# --------------------------
st.set_page_config(page_title="AI-assisted Symbolic Execution", layout="wide")
create_usertable()

# Initialize session variables
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "page" not in st.session_state:
    st.session_state.page = "login"

# --------------------------
# LOGIN PAGE
# --------------------------
def login_page():
    st.title("🔐 Login to AI-Assisted Symbolic Execution App")
    username = st.text_input("Username")
    password = st.text_input("Password", type='password')

    if st.button("Login"):
        hashed_pswd = make_hashes(password)
        result = login_user(username, hashed_pswd)

        if result:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.page = "main"
            st.success(f"✅ Welcome {username}!")
            st.experimental_rerun()
        else:
            st.warning("❌ Incorrect Username/Password")

    st.markdown("Don't have an account?")
    if st.button("Go to Sign Up"):
        st.session_state.page = "signup"
        st.experimental_rerun()

# --------------------------
# SIGNUP PAGE
# --------------------------
def signup_page():
    st.title("📝 Create a New Account")
    new_user = st.text_input("Choose a Username")
    new_password = st.text_input("Choose a Password", type='password')

    if st.button("Sign Up"):
        add_userdata(new_user, make_hashes(new_password))
        st.success("✅ Account created successfully!")
        st.info("Now go to Login to access the app.")
    if st.button("Go to Login"):
        st.session_state.page = "login"
        st.experimental_rerun()

# --------------------------
# MAIN APP PAGE
# --------------------------
def main_app():
    st.title("🤖 AI-assisted Symbolic Execution Demo")
    st.write(f"Welcome, **{st.session_state.username}** 👋")

    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.page = "login"
        st.experimental_rerun()

    st.markdown("""
    Upload a small C program. The app will:
    1. compile it,
    2. run symbolic execution (mocked on Cloud),
    3. apply a template patch and show the fixed code.
    """)

    # Paths
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    SRC_DIR = os.path.join(BASE_DIR, "..", "src")
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

# --------------------------
# PAGE ROUTING
# --------------------------
if st.session_state.page == "login":
    login_page()
elif st.session_state.page == "signup":
    signup_page()
elif st.session_state.page == "main":
    main_app()
