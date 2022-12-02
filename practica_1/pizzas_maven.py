import pandas as pd
import sys
import signal
from tabulate import tabulate


def extract():

    # Extrae los datos de los csv que contienen los pedidos, las pizzas y los ingredientes de las pizzas

    detalles_pedidos = pd.read_csv("order_details.csv", sep = ",", encoding = "UTF-8")
    pizzas = pd.read_csv("pizzas.csv", sep = ",", encoding = "UTF-8")
    ingredientes = pd.read_csv("pizza_types.csv", sep = ",", encoding = "LATIN-1")
    pedidos= pd.read_csv("orders.csv", encoding="LATIN-1")
    return detalles_pedidos, pizzas, ingredientes, pedidos

def transform(detalles_pedidos, pizzas, ingredientes, pedidos):

    # Recibe como parámetros los 4 dataframes, pedidos, pizzas, ingredientes y detalles de pedidos.
    # Devuelve un diccionario con los ingredientes a comprar semanalmente.

    #Ahora, vamos a generar el informe de cada dataframe
    csvs = ["order_details.csv", "pizzas.csv", "pizza_types.csv", "orders.csv"]
    dfs = [detalles_pedidos, pizzas, ingredientes, pedidos]
    
    for i in range(len(dfs)):

        print('Informe del csv',csvs[i],':\n')
        informe = dfs[i].isna().sum().to_frame().rename(columns={0: 'NaNs'})
        informe['Nulls'] = dfs[i].isnull().sum()
        informe['Porcentaje NaNs'] = informe['NaNs'] / dfs[i].shape[0] * 100
        informe['Porcentaje Nulls'] = informe['Nulls'] / dfs[i].shape[0] * 100
        informe['Data Type'] = dfs[i].dtypes
        print(tabulate(informe, headers='keys', tablefmt='psql'))
        print('\n')
        nombre_fout = 'informe_'+csvs[i][:-4]+'.csv'
        informe.to_csv(nombre_fout) 

    # Cogemos el número de veces que se ha pedido cada pizza en un año.
    # Ahora lo dividimos por 365 (tomamos parte entera) y multiplicamos por 7 para obtener el número de pizzas que se pide cada semana
    # A eso le sumamos 1 porque mejor que sobren pizzas que que falten

    n_sem_pizzas=dict()
    d_ingr = dict()

    for p in pizzas['pizza_id']:
        n_sem_pizzas[p] = int(detalles_pedidos[detalles_pedidos['pizza_id'] == p]['quantity'].sum() / 365 * 7) + 1

    # Cogemos los ingredientes de cada pizza y los pasamos a una lista
    # A continuación, cogemos cada ingrediente de la lista y lo añadimos al diccionario de ingredientes
    # Inicializamos el valor de cada ingrediente a 0.
    
    for ingrediente_bruto in ingredientes['ingredients']:
        lista = ingrediente_bruto.split(', ')
        for ingrediente in lista:
            d_ingr[ingrediente] = 0
    
    # Ahora, para cada pizza, cogemos los ingredientes que tiene y los multiplicamos por el número de veces que se pide esa pizza en una semana

    for pizza_bruto in n_sem_pizzas.keys():
        # Ahora procesamos el nombre de cada pizza para sacar por separado el nombre y el tamaño.
        # El nombre de la pizza está entre los dos primeros guiones bajos
        # El tamaño de la pizza está entre el segundo y el tercer guión bajo
        # Cogemos el tamaño de la pizza y lo convertimos a un número según la lista Multiplicador
        pizza = pizza_bruto.split('_')
        tam = pizza.pop(-1)
        pizza = '_'.join(pizza)
        multi = Multiplicador[Tamaño.index(tam)]
        # Para cada pizza saco sus ingredientes y los paso a una lista.
        # Busco cada ingrediente en el diccionario de ingredientes y le sumo el resultado de multiplicar el número de pizzas de 
        # ese tipo que se han pedido en una semana
        # por el multiplicador que le corresponde según su tamaño

        # Usamos map para convertir los ingredientes en una lista
        ingredientes_pizza = ingredientes[ingredientes['pizza_type_id'] == pizza]['ingredients'].item()
        lista = ingredientes_pizza.split(', ')
        list(map(lambda x: d_ingr.update({x: d_ingr[x] + n_sem_pizzas[pizza_bruto]*multi}), lista))
    
    return d_ingr

def load(d_ingr):
    
        # Recibe como parámetro el diccionario de ingredientes a comprar semanalmente.
        # Crea un dataframe con los ingredientes y sus cantidades y lo guarda en un csv.
        # Muestra por pantalla el dataframe.
        """
        compra_semana = pd.DataFrame([[key, d_ingr[key]] for key in d_ingr.keys()], columns=['Ingrediente', 'Unidades'])
        """
        compra_semana = pd.DataFrame(d_ingr.items(), columns=['Ingrediente', 'Unidades'])
        compra_semana.to_csv('compra_semana.csv', index=False)
        print('El dataframe con la cantidad de ingredientes a comprar semanalmente es:\n')
        # Imprimimos el dataframe de forma más bonita
        print(tabulate(compra_semana, headers='keys', tablefmt='psql'))

def handler_signal(signal, frame):
    print("\n [!] Se ha recibido la señal de interrupción. Finalizando ejecución...")
    sys.exit(1)

# Ctrl + C
signal.signal(signal.SIGINT, handler_signal)


Multiplicador = [1, 2, 3, 4, 5] # Esta lista da un peso a cada pizza según su tamaño
Tamaño = ['s','m','l','xl', 'xxl'] # Esta lista contiene los tamaños de las pizzas


if __name__ == "__main__":
    detalles_pedidos, pizzas, ingredientes, pedidos = extract()
    d_ingr = transform(detalles_pedidos, pizzas, ingredientes,pedidos)
    load(d_ingr)



    

    
