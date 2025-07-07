import os

CENTIUM_TXT = os.path.join(os.path.dirname(__file__), 'centium.txt')
OUTPUT_HTML = os.path.join(os.path.dirname(__file__), 'centium2.html')
IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')

# Read centium.txt into a list of (num, word)
def read_centium():
    entries = []
    with open(CENTIUM_TXT, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or ':' not in line:
                continue
            num, word = line.split(':', 1)
            entries.append((num.strip().zfill(2), word.strip()))
    return entries

def split_word(word):
    # Split word into main and parenthetical part
    if '(' in word and word.endswith(')'):
        main, paren = word.split('(', 1)
        main = main.strip()
        paren = '(' + paren  # add back the parenthesis
        return main, paren
    elif '(' in word:
        main, paren = word.split('(', 1)
        main = main.strip()
        paren = '(' + paren  # add back the parenthesis
        return main, paren
    else:
        return word, None

def main():
    entries = read_centium()
    table = [['' for _ in range(10)] for _ in range(10)]
    table_style = (
        "border-collapse:collapse;"
        "table-layout:fixed;"
        "width:2560px;"
        "height:2560px;"
    )
    cell_base_style = ""  # Now handled by CSS class
    for idx, (num, word) in enumerate(entries):
        x = idx // 10
        y = idx % 10
        img_path = os.path.join(IMG_DIR, f"{num}.png")
        if os.path.exists(img_path):
            bg_style = f"background: url('./img/{num}.png') center center / cover no-repeat, white;"
        else:
            bg_style = "background: white;"
            print(f"No image found for {num}: {word} in {img_path}")
        # Use class for cell, only background as style
        main_word, paren = split_word(word)
        if paren:
            word_html = f"<span class='word'>{main_word}</span> <span class='paren'>{paren}</span>"
        else:
            word_html = f"<span class='word'>{main_word}</span>"
        cell_html = f"""
        <div class='cell-content'>
            <div class='number'>{num}</div>
            <div class='word-container'>{word_html}</div>
        </div>
        """
        table[x][y] = f"<td class=\"centium-cell\" style=\"{bg_style}\">" + cell_html + "</td>"
    rows = []
    for row in table:
        row_html = ''.join(row)
        rows.append(f"<tr>{row_html}</tr>")
    # CSS classes for styling
    css = '''
    <style>
    .centium-cell {
        width:256px;
        height:256px;
        vertical-align:middle;
        text-align:center;
        border:1px solid #888;
        padding:0;
        position: relative;
    }
    .cell-content {
        display: flex;
        flex-direction: column;
        align-items: center;
        height: 100%;
        width: 100%;
        position: relative;
    }
    .number {
        position: absolute;
        top: 4px;
        left: 8px;
        color: black;
        font-size: 2em;
        text-align: left;
        /* White outline using multiple shadows */
        text-shadow:
            -1px -1px 0 #fff,
             1px -1px 0 #fff,
            -1px  1px 0 #fff,
             1px  1px 0 #fff,
            0   -1.5px 0 #fff,
            0    1.5px 0 #fff,
            -1.5px 0   0 #fff,
             1.5px 0   0 #fff;
        z-index: 2;
    }
    .word-container {
        position: absolute;
        top: 75%;
        left: 0;
        width: 100%;
        display: flex;
        flex-direction: column;
        align-items: center;
    }
    .word {
        color: white;
        font-weight: bold;
        font-size: 2em;
        text-align: center;
        text-shadow: 0 0 12px #000, 0 0 8px #000, 0 0 4px #000, 2px 2px 8px #000, -2px -2px 8px #000, 0 0 2px #fff;
    }
    .paren {
        color: white;
        font-size: 1.1em;
        text-align: center;
        text-shadow: 0 0 12px #000, 0 0 8px #000, 0 0 4px #000, 2px 2px 8px #000, -2px -2px 8px #000, 0 0 2px #fff;
        font-weight: normal;
    }
    </style>
    '''
    html_out = f"""
    <html><head><meta charset='utf-8'><title>Centium 10x10 Table</title>{css}</head>
    <body>
    <h1>Centium 10x10 Table</h1>
    <table style='{table_style}'>
      {''.join(rows)}
    </table>
    </body></html>
    """
    with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
        f.write(html_out)
    print(f"Wrote {OUTPUT_HTML}")

if __name__ == '__main__':
    main()
