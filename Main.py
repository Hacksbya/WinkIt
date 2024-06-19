import subprocess
import mysql.connector


def run_script(script_name, *args):
    try:
        subprocess.run(['python', script_name, *args], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing script '{script_name}': {e}")

# def authenticate_user(user_id):
#     try:
#         connection = mysql.connector.connect(host='localhost',
#                                              database='winkit_demo',
#                                              user='root',
#                                              password='Root')
#         cursor = connection.cursor()
#         cursor.execute("INSERT INTO Login_attempt (User_id) VALUES (%s)", (user_id,))
#         connection.commit()
#         cursor.close()
        
#     except mysql.connector.Error as error:
#         print(error)
#         return False
#     finally:
#         if 'connection' in locals() and connection.is_connected():
#             cursor.close()
#             connection.close()
        
#     return True

def authenticate_user(user_id):
    try:
        connection = mysql.connector.connect(host='localhost',
                                             database='winkit_demo',
                                             user='root',
                                             password='Root')

        if connection.is_connected():
            cursor = connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM User WHERE User_id = %s", (user_id,))
            user_count = cursor.fetchone()[0]
            if user_count == 1:
                return True
            else:
                print("User does not exist.")
                print("Try Again..")
                return False
    except mysql.connector.Error as error:
        print(error)
        return False
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

def main():
    print("Welcome to Winkit!")
    while True:
        print("1. Log In")
        print("2. Exit")
        t = input("Enter Your Choice : ")
        if t == '1':
            retry_count = 3
            logged_in = False  # Flag to indicate if the user is logged in
            while retry_count > 0:
                user_id = input("Enter User Id: ")
                if authenticate_user(user_id):
                    print("Authentication successful!")
                    logged_in = True
                    while True:
                        print("\nMenu")
                        print("1. Check Inventory")
                        print("2. Order Items")
                        print("3. Log Out")
                        choice = input("Enter your choice: ")
                        if choice == '1':
                            run_script('Analyze_inventory.py', user_id)
                        elif choice == '2':
                            run_script('Order_items.py', user_id)
                        elif choice == '3':
                            print("Logging you out...")
                            print("Exiting...")
                            logged_in = False  # Update flag
                            break  # Break out of the inner loop
                        else: 
                            print("Invalid choice. Please try again.")
                else:
                    retry_count -= 1
                    print(f"Authentication failed. {retry_count} attempts remaining.")
                if not logged_in:  # Check if user logged out successfully
                    break  # Break out of the inner loop and continue with the outer loop
            else:
                print("Maximum retry attempts reached. Exiting...")
                break  # Break out of the outer loop
        elif t == '2':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
