from auth import check_password
from utils import format_log_message

def start_app():
    print(format_log_message("Application starting up..."))
    is_valid = check_password("admin", "super_secret_123")
    print(format_log_message(f"Login status: {is_valid}"))

if __name__ == "__main__":
    start_app()
