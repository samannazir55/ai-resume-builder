import os

main_path = os.path.join("backend", "app", "main.py")

try:
    with open(main_path, "r", encoding="utf-8") as f:
        content = f.read()

    # The missing line
    import_line = "from .crud import init_db"

    # 1. Check if missing
    if "init_db.sync_templates" in content and "from .crud import init_db" not in content:
        # We need to add the import. 
        # Find the crud import line or just add it at top imports.
        if "from .crud import" in content:
            # We assume a structure like 'from .crud import user as user_crud...'
            # Let's just insert it cleanly as a separate line after logging import
            content = content.replace("import logging", "import logging\nfrom .crud import init_db")
        else:
            # Fallback
            content = "from .crud import init_db\n" + content
            
        with open(main_path, "w", encoding="utf-8") as f:
            f.write(content)
        print("✅ FIXED: Added missing 'init_db' import.")
        
    elif "init_db" not in content:
        print("⚠️ Warning: logic to call init_db is missing too.")
    else:
        print("ℹ️ Import seems present already (or checked logic matches).")

except Exception as e:
    print(f"❌ Error: {e}")