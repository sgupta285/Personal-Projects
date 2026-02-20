import os

# Files or folders to ignore (keeps the file from getting too big)
# Added 'env', '.venv', and 'assets' to prevent 1GB+ file sizes
IGNORE_LIST = {
    'node_modules', '.git', '.next', 'dist', 'build', '__pycache__', 
    '.DS_Store', 'env', '.venv', 'venv', 'target', 'vendor', '.cache',
    'images', 'assets', 'videos', 'public', 'out', 'bower_components'
}

# Only these extensions will be read by the script
ALLOWED_EXTENSIONS = {'.js', '.jsx', '.ts', '.tsx', '.py', '.html', '.css', '.json', '.md'}

def create_codebase_context(output_file='codebase_context.txt'):
    print("🚀 Scanning folders and building context...")
    count = 0
    
    with open(output_file, 'w', encoding='utf-8') as outfile:
        # Loop through every folder and file in your project
        for root, dirs, files in os.walk('.'):
            # Skip folders in the ignore list to keep the file size small
            dirs[:] = [d for d in dirs if d not in IGNORE_LIST]
            
            for file in files:
                # Only include logic-based code files
                if any(file.endswith(ext) for ext in ALLOWED_EXTENSIONS):
                    file_path = os.path.join(root, file)
                    outfile.write(f"\n--- FILE: {file_path} ---\n")
                    try:
                        with open(file_path, 'r', encoding='utf-8') as infile:
                            outfile.write(infile.read())
                        count += 1
                    except Exception as e:
                        outfile.write(f"[Error reading file: {e}]")
                    outfile.write("\n")

    print(f"✅ Success! Processed {count} files.")
    print(f"📍 Your codebase has been saved to: {os.path.abspath(output_file)}")

if __name__ == "__main__":
    create_codebase_context()