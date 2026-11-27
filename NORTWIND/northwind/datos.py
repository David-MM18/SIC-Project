import os
import pandas as pd
from config import DATOS

def cargar_datos():
    def leer(nombre):
        return pd.read_csv(os.path.join(DATOS, nombre), sep=';')

    employees = leer('Employees.csv')
    employees['Empleado'] = employees['FirstName'] + ' ' + employees['LastName']

    rewards = leer('Rewards.csv')
    rewards = rewards.dropna(subset=['EmployeeID']).copy()
    rewards['EmployeeID'] = rewards['EmployeeID'].astype(int)

    dfs = {
        'orders': leer('Orders.csv'),
        'order_details': leer('OrderDetails.csv'),
        'employees': employees,
        'products': leer('Products.csv'),
        'categories': leer('Categories.csv'),
        'customers': leer('Customers.csv'),
        'shippers': leer('Shippers.csv'),
        'rewards': rewards,
    }
    dfs['orders']['OrderDate'] = pd.to_datetime(dfs['orders']['OrderDate'], errors='coerce')
    return dfs

def enriquecer_order_details(dfs):
    od = dfs['order_details'].merge(
        dfs['products'][['ProductID', 'ProductName', 'Price', 'CategoryID', 'SupplierID']],
        on='ProductID', how='left')
    od['LineTotal'] = od['Quantity'] * od['Price']
    return od

def construir_df_full(dfs, od):
    df_full = (od
               .merge(dfs['orders'], on='OrderID', how='left')
               .merge(dfs['customers'], on='CustomerID', how='left')
               .merge(dfs['employees'][['EmployeeID', 'FirstName', 'LastName']], on='EmployeeID', how='left')
               .merge(dfs['categories'], on='CategoryID', how='left')
               .merge(dfs['shippers'], on='ShipperID', how='left'))
    
    df_full['EmployeeName'] = df_full['FirstName'] + ' ' + df_full['LastName']
    return df_full
