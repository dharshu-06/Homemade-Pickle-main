# """
# Application Entry Point - Run with: python run.py
# """

# import os
# from dotenv import load_dotenv
# from app import create_app

# load_dotenv()

# app = create_app()

# if __name__ == '__main__':
#     port = int(os.getenv('PORT', 5000))
#     debug = os.getenv('DEBUG', 'True') == 'True'

#     print(f"\n{'='*55}")
#     print("  🥒  HOMEMADE PICKLES & SNACKS  (DynamoDB)")
#     print(f"{'='*55}")
#     print(f"  URL   : http://localhost:{port}")
#     print(f"  Admin : admin / admin123")
#     print(f"{'='*55}\n")

#     app.run(host='0.0.0.0', port=port, debug=debug)



"""
Application Entry Point
Run with: python run.py
"""

import os
from dotenv import load_dotenv
from app import create_app

# Load environment variables
load_dotenv()

app = create_app()

if __name__ == "__main__":

    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("DEBUG", "True") == "True"

    print("\n" + "=" * 60)
    print("🥒  HOMEMADE PICKLES & SNACKS STORE")
    print("📦 Database : DynamoDB")
    print("=" * 60)

    print(f"🌐 URL        : http://localhost:{port}")
    print(f"👤 Admin User : {os.getenv('ADMIN_USERNAME','admin')}")
    print("=" * 60 + "\n")

    app.run(
        host="0.0.0.0",
        port=port,
        debug=debug
    )