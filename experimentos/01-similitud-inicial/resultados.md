# Resultados: similitud inicial

Modelo: `intfloat/multilingual-e5-small`. Títulos analizados: 11 de 11.

## Variante A

Prefijo de sinopsis: `passage: ` · prefijo de búsquedas libres: `query: `

### 1. Matriz de similitud

|  | matrix-1999 | truman-show-1998 | talos-principle-2014 | the-road-2009 | children-of-men-2006 | last-of-us-2013 | alien-1979 | event-horizon-1997 | dead-space-2008 | toy-story-1995 | stardew-valley-2016 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| matrix-1999 | 1.000 | 0.839 | 0.852 | 0.824 | 0.843 | 0.828 | 0.854 | 0.811 | 0.832 | 0.828 | 0.812 |
| truman-show-1998 | 0.839 | 1.000 | 0.825 | 0.822 | 0.822 | 0.817 | 0.822 | 0.797 | 0.818 | 0.823 | 0.838 |
| talos-principle-2014 | 0.852 | 0.825 | 1.000 | 0.828 | 0.826 | 0.829 | 0.834 | 0.826 | 0.827 | 0.812 | 0.824 |
| the-road-2009 | 0.824 | 0.822 | 0.828 | 1.000 | 0.859 | 0.847 | 0.837 | 0.814 | 0.823 | 0.811 | 0.848 |
| children-of-men-2006 | 0.843 | 0.822 | 0.826 | 0.859 | 1.000 | 0.862 | 0.834 | 0.798 | 0.807 | 0.813 | 0.834 |
| last-of-us-2013 | 0.828 | 0.817 | 0.829 | 0.847 | 0.862 | 1.000 | 0.847 | 0.827 | 0.847 | 0.817 | 0.818 |
| alien-1979 | 0.854 | 0.822 | 0.834 | 0.837 | 0.834 | 0.847 | 1.000 | 0.875 | 0.870 | 0.827 | 0.820 |
| event-horizon-1997 | 0.811 | 0.797 | 0.826 | 0.814 | 0.798 | 0.827 | 0.875 | 1.000 | 0.866 | 0.810 | 0.793 |
| dead-space-2008 | 0.832 | 0.818 | 0.827 | 0.823 | 0.807 | 0.847 | 0.870 | 0.866 | 1.000 | 0.812 | 0.809 |
| toy-story-1995 | 0.828 | 0.823 | 0.812 | 0.811 | 0.813 | 0.817 | 0.827 | 0.810 | 0.812 | 1.000 | 0.798 |
| stardew-valley-2016 | 0.812 | 0.838 | 0.824 | 0.848 | 0.834 | 0.818 | 0.820 | 0.793 | 0.809 | 0.798 | 1.000 |

### 2. Acierto top-2

| título | grupo | vecino 1 | vecino 2 | aciertos |
| --- | --- | --- | --- | --- |
| matrix-1999 | realidad_simulada | alien-1979 (0.854) | talos-principle-2014 (0.852) | 1/2 |
| truman-show-1998 | realidad_simulada | matrix-1999 (0.839) | stardew-valley-2016 (0.838) | 1/2 |
| talos-principle-2014 | realidad_simulada | matrix-1999 (0.852) | alien-1979 (0.834) | 1/2 |
| the-road-2009 | supervivencia | children-of-men-2006 (0.859) | stardew-valley-2016 (0.848) | 1/2 |
| children-of-men-2006 | supervivencia | last-of-us-2013 (0.862) | the-road-2009 (0.859) | 2/2 |
| last-of-us-2013 | supervivencia | children-of-men-2006 (0.862) | alien-1979 (0.847) | 1/2 |
| alien-1979 | terror_espacial | event-horizon-1997 (0.875) | dead-space-2008 (0.870) | 2/2 |
| event-horizon-1997 | terror_espacial | alien-1979 (0.875) | dead-space-2008 (0.866) | 2/2 |
| dead-space-2008 | terror_espacial | alien-1979 (0.870) | event-horizon-1997 (0.866) | 2/2 |

**Total: 13/18**

### 3. Separación

| media mismo grupo | media grupos distintos | diferencia |
| --- | --- | --- |
| 0.855 | 0.823 | 0.032 |

### 4. Vecino más cercano de cada juego

| juego | grupo | vecino más cercano | similitud | resultado |
| --- | --- | --- | --- | --- |
| talos-principle-2014 | realidad_simulada | matrix-1999 | 0.852 | mismo grupo |
| last-of-us-2013 | supervivencia | children-of-men-2006 | 0.862 | mismo grupo |
| dead-space-2008 | terror_espacial | alien-1979 | 0.870 | mismo grupo |
| stardew-valley-2016 | sin_relacion | the-road-2009 | 0.848 | película de otro grupo |

### 5. Outliers

| título | similitud máxima | con |
| --- | --- | --- |
| toy-story-1995 | 0.828 | matrix-1999 |
| stardew-valley-2016 | 0.848 | the-road-2009 |

### 6. Distribución de similitudes entre pares distintos

| mínimo | p25 | mediana | p75 | máximo |
| --- | --- | --- | --- | --- |
| 0.793 | 0.815 | 0.826 | 0.838 | 0.875 |

### 7. Búsquedas libres (top-3)

| consulta | 1° | 2° | 3° |
| --- | --- | --- | --- |
| "a man discovers his whole life is fake" | truman-show-1998 (0.822) | the-road-2009 (0.803) | matrix-1999 (0.792) |
| "a father protects his son in a dying world" | the-road-2009 (0.881) | children-of-men-2006 (0.828) | stardew-valley-2016 (0.810) |
| "crew members hunted by a creature on a spaceship" | alien-1979 (0.866) | event-horizon-1997 (0.840) | dead-space-2008 (0.832) |

## Variante B

Prefijo de sinopsis: `query: ` · prefijo de búsquedas libres: `query: `

### 1. Matriz de similitud

|  | matrix-1999 | truman-show-1998 | talos-principle-2014 | the-road-2009 | children-of-men-2006 | last-of-us-2013 | alien-1979 | event-horizon-1997 | dead-space-2008 | toy-story-1995 | stardew-valley-2016 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| matrix-1999 | 1.000 | 0.849 | 0.864 | 0.834 | 0.846 | 0.833 | 0.863 | 0.829 | 0.840 | 0.833 | 0.830 |
| truman-show-1998 | 0.849 | 1.000 | 0.838 | 0.831 | 0.832 | 0.827 | 0.837 | 0.818 | 0.828 | 0.834 | 0.851 |
| talos-principle-2014 | 0.864 | 0.838 | 1.000 | 0.833 | 0.835 | 0.834 | 0.848 | 0.841 | 0.836 | 0.824 | 0.834 |
| the-road-2009 | 0.834 | 0.831 | 0.833 | 1.000 | 0.862 | 0.850 | 0.842 | 0.826 | 0.830 | 0.817 | 0.855 |
| children-of-men-2006 | 0.846 | 0.832 | 0.835 | 0.862 | 1.000 | 0.868 | 0.847 | 0.816 | 0.821 | 0.824 | 0.848 |
| last-of-us-2013 | 0.833 | 0.827 | 0.834 | 0.850 | 0.868 | 1.000 | 0.855 | 0.838 | 0.846 | 0.829 | 0.831 |
| alien-1979 | 0.863 | 0.837 | 0.848 | 0.842 | 0.847 | 0.855 | 1.000 | 0.890 | 0.877 | 0.836 | 0.843 |
| event-horizon-1997 | 0.829 | 0.818 | 0.841 | 0.826 | 0.816 | 0.838 | 0.890 | 1.000 | 0.875 | 0.828 | 0.818 |
| dead-space-2008 | 0.840 | 0.828 | 0.836 | 0.830 | 0.821 | 0.846 | 0.877 | 0.875 | 1.000 | 0.822 | 0.825 |
| toy-story-1995 | 0.833 | 0.834 | 0.824 | 0.817 | 0.824 | 0.829 | 0.836 | 0.828 | 0.822 | 1.000 | 0.817 |
| stardew-valley-2016 | 0.830 | 0.851 | 0.834 | 0.855 | 0.848 | 0.831 | 0.843 | 0.818 | 0.825 | 0.817 | 1.000 |

### 2. Acierto top-2

| título | grupo | vecino 1 | vecino 2 | aciertos |
| --- | --- | --- | --- | --- |
| matrix-1999 | realidad_simulada | talos-principle-2014 (0.864) | alien-1979 (0.863) | 1/2 |
| truman-show-1998 | realidad_simulada | stardew-valley-2016 (0.851) | matrix-1999 (0.849) | 1/2 |
| talos-principle-2014 | realidad_simulada | matrix-1999 (0.864) | alien-1979 (0.848) | 1/2 |
| the-road-2009 | supervivencia | children-of-men-2006 (0.862) | stardew-valley-2016 (0.855) | 1/2 |
| children-of-men-2006 | supervivencia | last-of-us-2013 (0.868) | the-road-2009 (0.862) | 2/2 |
| last-of-us-2013 | supervivencia | children-of-men-2006 (0.868) | alien-1979 (0.855) | 1/2 |
| alien-1979 | terror_espacial | event-horizon-1997 (0.890) | dead-space-2008 (0.877) | 2/2 |
| event-horizon-1997 | terror_espacial | alien-1979 (0.890) | dead-space-2008 (0.875) | 2/2 |
| dead-space-2008 | terror_espacial | alien-1979 (0.877) | event-horizon-1997 (0.875) | 2/2 |

**Total: 13/18**

### 3. Separación

| media mismo grupo | media grupos distintos | diferencia |
| --- | --- | --- |
| 0.864 | 0.834 | 0.030 |

### 4. Vecino más cercano de cada juego

| juego | grupo | vecino más cercano | similitud | resultado |
| --- | --- | --- | --- | --- |
| talos-principle-2014 | realidad_simulada | matrix-1999 | 0.864 | mismo grupo |
| last-of-us-2013 | supervivencia | children-of-men-2006 | 0.868 | mismo grupo |
| dead-space-2008 | terror_espacial | alien-1979 | 0.877 | mismo grupo |
| stardew-valley-2016 | sin_relacion | the-road-2009 | 0.855 | película de otro grupo |

### 5. Outliers

| título | similitud máxima | con |
| --- | --- | --- |
| toy-story-1995 | 0.836 | alien-1979 |
| stardew-valley-2016 | 0.855 | the-road-2009 |

### 6. Distribución de similitudes entre pares distintos

| mínimo | p25 | mediana | p75 | máximo |
| --- | --- | --- | --- | --- |
| 0.816 | 0.828 | 0.834 | 0.847 | 0.890 |

### 7. Búsquedas libres (top-3)

| consulta | 1° | 2° | 3° |
| --- | --- | --- | --- |
| "a man discovers his whole life is fake" | truman-show-1998 (0.792) | matrix-1999 (0.773) | the-road-2009 (0.770) |
| "a father protects his son in a dying world" | the-road-2009 (0.856) | children-of-men-2006 (0.802) | stardew-valley-2016 (0.794) |
| "crew members hunted by a creature on a spaceship" | alien-1979 (0.871) | event-horizon-1997 (0.850) | dead-space-2008 (0.834) |

## RAM del proceso (RSS)

| momento | MB |
| --- | --- |
| inicio del script | 30 |
| antes de cargar el modelo (con librerías importadas) | 388 |
| después de cargar el modelo | 1174 |
| después de generar los embeddings | 1222 |

Carga del modelo: +786 MB. Total desde el inicio: +1192 MB.

## Comparación de variantes

| variante | acierto top-2 | media mismo grupo | media grupos distintos | diferencia |
| --- | --- | --- | --- | --- |
| A | 13/18 | 0.855 | 0.823 | 0.032 |
| B | 13/18 | 0.864 | 0.834 | 0.030 |
