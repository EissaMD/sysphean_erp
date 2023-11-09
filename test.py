from resources import DB , CustomerManagement

db = DB()
db.connect()

cm = CustomerManagement(True)
cm.confirm_btn(True)

# query = 'INSERT INTO customer (name, email, contact, credit_limit, payment_terms, communication_preferences, shipping_address, billing_address) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);'
# data = ("customer_test" , "customer_test@example.com" , "0110000000" , "101010" , "Cash" , "Phone" , "MY" , "MY")
# db.cursor.execute(query, data)
# db