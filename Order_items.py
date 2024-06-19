import mysql.connector
import sys

def read_globals():
    with open('globals.txt', 'r') as file:
        data = file.read().splitlines()
        x = int(data[0])
        p = int(data[1])
    return x, p


def write_globals(x, p):
    with open('globals.txt', 'w') as file:
        file.write(str(x) + '\n')
        file.write(str(p) + '\n')

def order_items(user_id, items):
    try:
        connection = mysql.connector.connect(host='localhost',
                                             database='winkit_demo',
                                             user='root',
                                             password='Root')

        if connection.is_connected():
            cursor = connection.cursor()
            x, p = read_globals()
            # Get branch ID
            cursor.execute("SELECT Branch_id FROM Branch WHERE Pincode = (SELECT Pincode FROM User WHERE User_id = %s)", (user_id,))
            branch_id = cursor.fetchone()[0]

            total_price = 0
            order_details = []

            for item_id, quantity in items:
                # Check available quantity
                cursor.execute("SELECT Quantity FROM Inventory WHERE Branch_id = %s AND Item_id = %s", (branch_id, item_id))
                available_quantity = cursor.fetchone()
                if available_quantity is None:
                    print(f"Item {item_id} is out of stock.")
                    continue
                elif available_quantity[0] < quantity:
                    print(f"Only {available_quantity[0]} items of {item_id} available. Please order a lower quantity.")
                    continue

                # Get item details
                cursor.execute("SELECT Name, Description, Price FROM Item WHERE Item_id = %s", (item_id,))
                item_info = cursor.fetchone()
                if item_info:
                    item_name, description, price = item_info
                    total_price += quantity * price
                    order_details.append((item_id, item_name, description, quantity, price))

            # Output order details
            if order_details:
                print("\nOrder Details:")
                print("{:<10} {:<20} {:<30} {:<10} {:<10}".format("Item ID", "Item Name", "Description", "Quantity", "Price"))
                for item_id, item_name, description, quantity, price in order_details:
                    print("{:<10} {:<20} {:<30} {:<10} {:<10}".format(item_id, item_name, description, quantity, price))
                print("Total Price:", total_price)

                confirm_order = input("Do you want to confirm this order? (yes/no): ")
                if confirm_order.lower() == "yes":
                    # Insert order into Order_table
                    cursor.execute("INSERT INTO Order_table (Order_id, User_id, Branch_id, order_date, status) VALUES (%s,%s, %s, CURDATE(), 'pending')",(f"hjgx{x}",user_id,branch_id))
                    for item_id, _, _, quantity, _ in order_details:
                        cursor.execute("INSERT INTO Transaction(Transaction_id, Order_id, Item_id, Quantity) VALUES (%s,%s, %s, %s)",(f"T{p}",f"hjgx{x}",item_id,quantity))
                        p =int(p) 
                        p+=1
                        p = str(p)
                    for item_id, _, _, quantity, _ in order_details:
                        cursor.execute("UPDATE Inventory SET Quantity = Quantity - %s WHERE Branch_id = %s AND Item_id = %s", (quantity, branch_id, item_id))
                    connection.commit()
                    print("Order confirmed!")
                    x+=1
                    write_globals(x, p)
                else:
                    print("Order not confirmed.")
            else:
                print("No items available for order.")

    except mysql.connector.Error as error:
        print(error)
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python Order_items.py <user_id>")
        sys.exit(1)
    user_id = sys.argv[1]

    items = []
    while True:
        item_id = input("Enter Item id (or type 'done' to finish): ")
        if item_id.lower() == 'done':
            break
        quantity = int(input("Enter quantity: "))
        items.append((item_id, quantity))

    if items:
        order_items(user_id, items)
