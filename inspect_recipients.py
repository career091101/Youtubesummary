from src.config import Config

def inspect_recipients():
    if not Config.validate():
        print("Config validation failed.")
        # Continue anyway to see what we have
    
    recipients = Config.EMAIL_RECIPIENT
    print(f"Current EMAIL_RECIPIENT: {recipients}")
    
    if recipients and ',' in recipients:
        print("Multiple recipients detected.")
        addr_list = [addr.strip() for addr in recipients.split(',')]
        print(f"Parsed list: {addr_list}")
    else:
        print("Single recipient or empty.")

if __name__ == "__main__":
    inspect_recipients()
