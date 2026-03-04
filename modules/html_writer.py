from modules.preprocessing import is_incomplete

def write_html(results, roeper=False):
    def get_symbol(source):
        if roeper:
            return "✅" if source == "youtube" else "❌"
        return {
            "youtube": "📺",
            "web": "🌐",
            "both": "✅"}.get(source, "❌")

    def get_class_and_checked(match_type, video):
        if match_type == "match":      
            if video and is_incomplete(video):
                return "incomplete", ""
            return "match", "checked"
        return "no-match", ""
    
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Match Results</title>
        <style>
            body { font-family: Arial, sans-serif; }
            .match { color: green; font-weight: bold; }
            .no-match { color: red; font-weight: bold; }
            .incomplete { color: orange; font-weight: bold; }
            .checkbox { margin-right: 10px; }
        </style>
        <script>
            function toggleMatch(checkbox, listItem) {
                if (checkbox.checked) {
                    listItem.classList.remove("no-match");
                    listItem.classList.add("match");
                } else {
                    listItem.classList.remove("match");
                    listItem.classList.add("no-match");
                }
            }
        </script>
    </head>
    <body>
        <h2>Match Results</h2>
        <ul>
    """
    for i, (web_episode, video_match, match_type, source, _) in enumerate(results, start=1):
        symbol = get_symbol(source)
        css_class, checked = get_class_and_checked(match_type, video_match)
        item_id = web_episode.replace(" ", "_")
        
        # Ensure numbering starts at 1 in the HTML output by stripping original number if present
        parts = web_episode.split(" ", 1)
        if len(parts) > 1 and parts[0].isdigit():
            title_text = parts[1]
        else:
            title_text = web_episode
        
        display_title = f"{i} {title_text}"
        content = f"{display_title} → {video_match}" if match_type == "match" else display_title
        html_content += f'''
            <li id="{item_id}" class="{css_class}">
                <input type="checkbox" class="checkbox" {checked} 
                onclick="toggleMatch(this, this.parentElement)">
                {content} {symbol}
            </li>\n'''

    html_content += """
        </ul>
    </body>
    </html>
    """
    
    f =  open("semantic_matches.html", "w+", encoding="utf-8")
    filename = "roeper_matches.html" if roeper else "semantic_matches.html"
    f =  open(filename, "w+", encoding="utf-8")
    f.write(html_content)
    f.seek(0)  #Resets the pointer
    print("✅ File 'semantic_matches.html' generated with colors and checkboxes.")
    print(f"✅ File '{filename}' generated with colors and checkboxes.")
    return f