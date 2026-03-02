from modules.preprocessing import is_incomplete

def write_html(results):
    def get_symbol(source):
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
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Resultados de Coincidencias</title>
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
        <h2>Resultados de Coincidencias</h2>
        <ul>
    """
    for web_episode, video_match, match_type, source, _ in results:
        symbol = get_symbol(source)
        css_class, checked = get_class_and_checked(match_type, video_match)
        item_id = web_episode.replace(" ", "_")
        content = f"{web_episode} → {video_match}" if match_type == "match" else web_episode
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
    f.write(html_content)
    f.seek(0)  #Resets the pointer
    print("✅ File 'semantic_matches.html' generated with colors and checkboxes.")
    return f