def calcular_top_ordenes(dfs):
    conteo = dfs['orders'].groupby('EmployeeID').size()
    df = dfs['employees'][['EmployeeID', 'Empleado']].copy()
    df['TotalVentas'] = df['EmployeeID'].map(conteo).fillna(0).astype(int)
    return df.sort_values('TotalVentas', ascending=True)[['Empleado', 'TotalVentas']]

def calcular_top_productos(dfs):
    df = dfs['order_details'].merge(dfs['products'][['ProductID', 'ProductName']], on='ProductID')
    df = df.groupby('ProductName', as_index=False).agg(UnidadesVendidas=('Quantity', 'sum'))
    df = df.nlargest(10, 'UnidadesVendidas')[['ProductName', 'UnidadesVendidas']]
    return df.sort_values('UnidadesVendidas')

def calcular_top_beneficio(dfs):
    df = dfs['order_details'].merge(dfs['products'], on='ProductID')
    df = df.groupby('ProductName', as_index=False).agg({'Quantity': 'sum', 'Price': 'first'})
    df['TotalBeneficio'] = df['Quantity'] * df['Price']
    df = df.nlargest(10, 'TotalBeneficio')[['ProductName', 'TotalBeneficio']]
    return df.sort_values('TotalBeneficio')

def calcular_top_recaudado(dfs):
    df = dfs['employees'].merge(dfs['orders'], on='EmployeeID', how='left')
    df = df.merge(dfs['order_details'], on='OrderID', how='left')
    df = df.merge(dfs['products'], on='ProductID', how='left')
    df['TotalRecaudado'] = df['Quantity'] * df['Price']
    df = df.groupby(['EmployeeID', 'Empleado'], as_index=False)[['TotalRecaudado']].sum()
    return df.sort_values('TotalRecaudado', ascending=True)[['Empleado', 'TotalRecaudado']]