import matplotlib.pyplot as plt
import pandas as pd
import sqlite3


with sqlite3.connect(r'C:\Users\HENRY\Desktop\CURSOS DALTO\SQL\NORTWIND\Northwind.db') as conn:
    cursor = conn.cursor()
    cursor.execute('''
                   SELECT (FirstName || ' ' || LastName) AS Empleado, COALESCE(COUNT(Orders.EmployeeID), 0) AS TotalVentas FROM Orders
                   RIGHT JOIN Employees ON Employees.EmployeeID = Orders.EmployeeID
                   GROUP BY Orders.EmployeeID
                   ORDER BY Empleado
                   ''')
    empleados = pd.DataFrame(cursor.fetchall(), columns=['Empleado', 'TotalVentas'])
    cursor.execute('''
                   SELECT ProductName, SUM(Quantity) AS UnidadesVendidas FROM Products
                   JOIN OrderDetails ON OrderDetails.ProductID = Products.ProductID
                   GROUP BY Products.ProductID
                   ORDER BY UnidadesVendidas DESC
                   LIMIT 10
                   ''')
    cantidades_ventas = pd.DataFrame(cursor.fetchall(), columns=['Articulo', 'UnidadesVendidas'])
    cursor.execute('''
                   SELECT ProductName AS Articulo, ROUND(SUM(Quantity) * Price, 2) AS BeneficioTotal FROM Products
                   JOIN OrderDetails ON OrderDetails.ProductID = Products.ProductID
                   GROUP BY Products.ProductID
                   ORDER BY BeneficioTotal DESC
                   LIMIT 10
                   ''')
    total_beneficios = pd.DataFrame(cursor.fetchall(), columns=['Articulo', 'BeneficioTotal'])


# Gráfico 1: Top Vendedores Más Exitosos
plt.figure(figsize=(8, 5))
plt.barh(empleados['Empleado'], empleados['TotalVentas'], color='skyblue')

plt.title('Top Vendedores')
plt.xlabel('Total de Ventas')
plt.ylabel('Empleados')
# plt.xticks(rotation=35, ha='right')

plt.tight_layout()
plt.savefig('vendedores.png', dpi=300)


# Gráfico 2: Top Artículos Más Vendidos
plt.figure(figsize=(8, 5))
plt.barh(cantidades_ventas['Articulo'], cantidades_ventas['UnidadesVendidas'], color='green')

plt.title('Top Artículos Más Vendidos')
plt.xlabel('UnidadesVendidas')
plt.ylabel('Articulo')
# plt.xticks(rotation=35, ha='right')

plt.tight_layout()
plt.savefig('vendidos.png', dpi=300)


# Gráfico 3: Top Beneficios De Cada Artículo
plt.figure(figsize=(8, 5))
plt.barh(total_beneficios['Articulo'], total_beneficios['BeneficioTotal'], color='orange')

plt.title('Top Beneficios De Cada Artículo')
plt.xlabel('BeneficioTotal')
plt.ylabel('Articulo')
# plt.xticks(rotation=35, ha='right')

plt.tight_layout()
plt.savefig('beneficios.png', dpi=300)
