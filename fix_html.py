import sys

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # We will search for all st.markdown(...) blocks and strip leading spaces of HTML lines inside strings
    # But wait, it's easier to just replace `st.markdown(dedent(f"""` with `st.markdown(f"""`
    # and for each block, just lstrip all lines
    
    # Actually, let's just create a custom function to render html in Streamlit 1.28.2
    # and replace st.markdown(..., unsafe_allow_html=True) with it.
    
    # Read the lines
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    out = []
    i = 0
    while i < len(lines):
        # We replace the dedent call
        if 'st.markdown(dedent(f"""' in lines[i]:
            out.append(lines[i].replace('st.markdown(dedent(f"""', 'render_html(f"""'))
            i += 1
            continue
            
        if 'unsafe_allow_html=True)' in lines[i]:
            if 'st.markdown' in lines[i]:
                out.append(lines[i].replace('st.markdown', 'render_html').replace(', unsafe_allow_html=True', ''))
            elif 'unsafe_allow_html=True' in lines[i] and 'render_html' in out[-1]:
                # already replaced st.markdown on a previous line, just remove unsafe_allow_html
                out.append(lines[i].replace(', unsafe_allow_html=True', ''))
            elif 'unsafe_allow_html=True' in lines[i] and 'st.markdown' in out[-1]:
                # multiline st.markdown call?
                out[-1] = out[-1].replace('st.markdown', 'render_html')
                out.append(lines[i].replace(', unsafe_allow_html=True', ''))
            else:
                out.append(lines[i].replace(', unsafe_allow_html=True', ''))
            i += 1
            continue

        if 'st.markdown(f"""' in lines[i]:
            # we will assume the ending line has unsafe_allow_html=True
            out.append(lines[i].replace('st.markdown(f"""', 'render_html(f"""'))
            i += 1
            continue

        if 'st.markdown("""' in lines[i]:
            out.append(lines[i].replace('st.markdown("""', 'render_html("""'))
            i += 1
            continue

        if 'st.markdown(loading_html' in lines[i]:
            out.append(lines[i].replace('st.markdown', 'render_html').replace(', unsafe_allow_html=True', ''))
            i += 1
            continue

        if '<div style=' in lines[i] or '<span style=' in lines[i]:
            # It's an HTML line inside f-string. Let's make sure it doesn't have 4 spaces.
            pass
            
        out.append(lines[i])
        i += 1

    # Insert the render_html definition at the top
    # Let's find imports
    insert_idx = 0
    for idx, line in enumerate(out):
        if 'import streamlit as st' in line:
            insert_idx = idx + 1
            break
            
    helper = """
def render_html(html_str):
    if not isinstance(html_str, str):
        st.markdown(html_str, unsafe_allow_html=True)
        return
    # Strip leading whitespace to avoid markdown parsing as code blocks
    cleaned = "\\n".join(line.lstrip() for line in html_str.split("\\n"))
    st.markdown(cleaned, unsafe_allow_html=True)
"""
    out.insert(insert_idx, helper)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(out)

if __name__ == '__main__':
    process_file('app/main.py')
