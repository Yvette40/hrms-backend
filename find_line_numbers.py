"""
Find Line Numbers Script
This script just tells you which lines to delete - it doesn't modify anything
"""

def find_duplicate_section():
    """Find and print the line numbers of the duplicate section"""
    
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        print("=" * 60)
        print("LINE NUMBER FINDER")
        print("=" * 60)
        print(f"\n📊 Your app.py has {len(lines)} total lines\n")
        
        # Find start line
        start_line = -1
        for i, line in enumerate(lines):
            if "@app.route('/test-email')" in line:
                start_line = i
                break
        
        # Find end line
        end_line = -1
        if start_line != -1:
            for i in range(start_line, len(lines)):
                if '@app.route("/leave-requests"' in lines[i]:
                    end_line = i - 1
                    while end_line > start_line and lines[end_line].strip() == '':
                        end_line -= 1
                    break
        
        if start_line == -1:
            print("✅ Good news! Could not find duplicate section.")
            print("   Your file might already be fixed!")
            return
        
        if end_line == -1:
            print("⚠️  Found start but not end. Manual inspection needed.")
            print(f"   Start line: {start_line + 1}")
            return
        
        # Print the results
        print("🎯 FOUND DUPLICATE SECTION!")
        print("-" * 60)
        print(f"📍 DELETE FROM LINE: {start_line + 1}")
        print(f"📍 DELETE TO LINE:   {end_line + 1}")
        print(f"📊 TOTAL LINES TO DELETE: {end_line - start_line + 1}")
        print("-" * 60)
        
        # Show context
        print("\n📋 START OF SECTION TO DELETE (Line {}):".format(start_line + 1))
        print("-" * 60)
        for i in range(start_line, min(start_line + 5, len(lines))):
            print(f"{i+1:4d} | {lines[i]}", end='')
        print("     | ... (many more lines) ...")
        
        print("\n📋 END OF SECTION TO DELETE (Line {}):".format(end_line + 1))
        print("-" * 60)
        for i in range(max(end_line - 4, start_line), end_line + 1):
            print(f"{i+1:4d} | {lines[i]}", end='')
        
        print("\n📋 KEEP THIS (Don't delete, Line {}):".format(end_line + 2))
        print("-" * 60)
        if end_line + 1 < len(lines):
            for i in range(end_line + 1, min(end_line + 4, len(lines))):
                print(f"{i+1:4d} | {lines[i]}", end='')
        
        print("\n" + "=" * 60)
        print("INSTRUCTIONS:")
        print("=" * 60)
        print(f"1. Open app.py in your editor")
        print(f"2. Go to line {start_line + 1}")
        print(f"3. Select from line {start_line + 1} to line {end_line + 1}")
        print(f"4. Delete the selected lines")
        print(f"5. Save the file")
        print(f"6. Run: python app.py")
        print("=" * 60)
        
    except FileNotFoundError:
        print("❌ Error: app.py not found in current directory")
        print("📁 Please run this script from your project root")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    find_duplicate_section()
