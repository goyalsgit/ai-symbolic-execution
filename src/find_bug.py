# find_bug.py
# A short angr script that treats the command-line argument as symbolic
# and searches for a run that prints "CRASH".
# Note: requires angr installed in your Python environment.
import angr, claripy

proj = angr.Project('./bugprog', auto_load_libs=False)

# We'll allow the argument to be up to 4 characters long (enough for "0")
arg_size = 4
sym_arg = claripy.BVS('arg', 8 * arg_size)  # symbolic byte-vector

# Create the initial state with a symbolic argv[1]
state = proj.factory.entry_state(args=['./bugprog', sym_arg])

# Create a simulation manager to explore program paths
simgr = proj.factory.simgr(state)

# Define the condition that identifies the crashing path:
# we look for states whose stdout contains the string 'CRASH'
def is_crash(s):
    try:
        out = s.posix.dumps(1)  # stdout
        return b'CRASH' in out
    except Exception:
        return False

# Explore the program until we find a state that triggered CRASH
simgr.explore(find=is_crash, num_find=1)

if simgr.found:
    found = simgr.found[0]
    # Ask the solver for a concrete value for the symbolic argument
    concrete_bytes = found.solver.eval(sym_arg, cast_to=bytes)
    # remove trailing null bytes and decode to string
    concrete = concrete_bytes.split(b'\x00')[0].decode(errors='ignore')
    print('Found argument that causes CRASH:', repr(concrete))
else:
    print('No crashing input found.')
