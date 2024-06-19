import mysql.connector
import sys

def find_branch_id(user_id):
    try:
        connection = mysql.connector.connect(host='localhost',
                                             database='winkit_demo',
                                             user='root',
                                             password='Root')
        if connection.is_connected():
            cursor = connection.cursor()
            cursor.execute("SELECT Branch_id FROM Branch WHERE Pincode = (SELECT Pincode FROM User WHERE User_id = %s)", (user_id,))
            branch_id = cursor.fetchone()
            if branch_id:
                return branch_id[0]
            else:
                print("We are not currently serving your region.")
                return None
    except mysql.connector.Error as error:
        print("Error:", error)
        return None
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

def analyze_inventory(user_id):
    branch_id = find_branch_id(user_id)
    if branch_id:
        try:
            connection = mysql.connector.connect(host='localhost',
                                                 database='winkit_demo',
                                                 user='root',
                                                 password='Root')
            if connection.is_connected():
                cursor = connection.cursor()

                # Retrieve available items in the inventory for the specified branch
                cursor.execute("""
                    SELECT Item.Item_id, Item.Name, Item.Description, 
                           CASE WHEN Inventory.Quantity > 0 THEN 'In Stock' ELSE 'Out of Stock' END AS Availability
                    FROM Item
                    LEFT JOIN Inventory ON Item.Item_id = Inventory.Item_id AND Inventory.Branch_id = %s
                """, (branch_id,))
                
                rows = cursor.fetchall()

                if rows:
                    print("Item details:")
                    for row in rows:
                        item_id, name, description, availability = row
                        print(f"Item ID: {item_id}")
                        print(f"Name: {name}")
                        print(f"Description: {description}")
                        print(f"Availability: {availability}")
                        print()
                else:
                    print("No items found in the inventory for the specified branch.")

        except mysql.connector.Error as error:
            print("Error:", error)
        finally:
            if 'connection' in locals() and connection.is_connected():
                cursor.close()
                connection.close()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python analyze_inventory.py <user_id>")
        sys.exit(1)

    user_id = sys.argv[1]
    analyze_inventory(user_id)