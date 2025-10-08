# auto_patch.py
# A simple automated patcher that shows two modes:
# 1) template-based repair (safe default)
# 2) optional AI-assisted repair using OpenAI API if the user provides an API key
#
# Usage:
#   python3 auto_patch.py --mode template bugprog.c bugprog_fixed_auto.c
#   python3 auto_patch.py --mode ai --openai-key YOUR_KEY bugprog.c bugprog_fixed_ai.c

import argparse, re, sys, subprocess, os, textwrap

TEMPLATE_PATCH = '''
/* AUTO-PATCH (template): add guard for division-by-zero */
if (x == 0) {
    printf("Input was 0, auto-patched to avoid division.\\n");
    return 1;
}
'''

AI_PROMPT = (
'You are an assistant that suggests a small C patch to fix a bug.\n'
'The input is the source file content. Produce only the replacement code block\n'
'to insert where a division by a user-provided integer is unsafe.\n'
)

def apply_template_patch(src_text):
    # naive: find the first occurrence of 'int x = atoi(argv[1]);' and insert guard after it
    pattern = r'(int\s+x\s*=\s*atoi\(argv\[1\]\);)'
    m = re.search(pattern, src_text)
    if not m:
        raise RuntimeError("Could not find the expected pattern to patch.")
    insert_pos = m.end()
    new_text = src_text[:insert_pos] + "\n    " + TEMPLATE_PATCH + src_text[insert_pos:]
    return new_text

def call_openai_api(prompt, api_key):
    import openai
    openai.api_key = api_key
    resp = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=200,
        temperature=0.0
    )
    return resp['choices'][0]['text']

def apply_ai_patch(src_text, api_key):
    # craft prompt with the source
    prompt = AI_PROMPT + "\n\n=== SOURCE ===\n" + src_text + "\n\n=== PATCH ===\n"
    patch = call_openai_api(prompt, api_key)
    # naive application: insert patch after atoi line
    pattern = r'(int\s+x\s*=\s*atoi\(argv\[1\]\);)'
    m = re.search(pattern, src_text)
    if not m:
        raise RuntimeError("Could not find insertion point for AI patch.")
    insert_pos = m.end()
    new_text = src_text[:insert_pos] + "\n    " + patch.strip() + "\n" + src_text[insert_pos:]
    return new_text

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('src', help='source file to patch')
    parser.add_argument('dst', help='output patched file')
    parser.add_argument('--mode', choices=['template','ai'], default='template')
    parser.add_argument('--openai-key', help='OpenAI API key (for ai mode)', default=os.environ.get('OPENAI_API_KEY'))
    args = parser.parse_args()

    src_text = open(args.src).read()

    if args.mode == 'template':
        patched = apply_template_patch(src_text)
    else:
        if not args.openai_key:
            print("AI mode requires --openai-key or OPENAI_API_KEY env var.", file=sys.stderr)
            sys.exit(1)
        patched = apply_ai_patch(src_text, args.openai_key)

    open(args.dst, 'w').write(patched)
    print("Patched file written to", args.dst)

if __name__ == '__main__':
    main()
