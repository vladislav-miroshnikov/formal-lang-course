# Описание языка запросов к графам

## Описание абстрактного синтаксиса языка

```
prog = List<stmt>
stmt =
    bind of var * expr
  | print of expr
  
val =
    String of string
  | Int of int
  | Bool of bool
  | Path of path
  | List of string
  | List of int
  | List of bool
  
expr =
    Var of var                   // переменные
  | Val of val                   // константы
  | Set_start of Set<val> * expr // задать множество стартовых состояний
  | Set_final of Set<val> * expr // задать множество финальных состояний
  | Add_start of Set<val> * expr // добавить состояния в множество стартовых
  | Add_final of Set<val> * expr // добавить состояния в множество финальных
  | Get_start of expr            // получить множество стартовых состояний
  | Get_final of expr            // получить множество финальных состояний
  | Get_reachable of expr        // получить все пары достижимых вершин
  | Get_vertices of expr         // получить все вершины
  | Get_edges of expr            // получить все рёбра
  | Get_labels of expr           // получить все метки
  | Map of lambda * expr         // классический map
  | Filter of lambda * expr      // классический filter
  | Load of path                 // загрузка графа
  | Intersect of expr * expr     // пересечение языков
  | Concat of expr * expr        // конкатенация языков
  | Union of expr * expr         // объединение языков
  | Star of expr                 // замыкание языков (звезда Клини)
  | Smb of expr                  // единичный переход

lambda =
    Lambda of List<var> * expr
```

### Описание конкретного синтаксиса языка
```
PROGRAM -> STMT ; PROGRAM | eps
STMT -> VAR = EXPR | print(EXPR)

LOWERCASE -> [a-z]
UPPERCASE -> [A-Z]
DIGIT -> [0-9]

INT -> 0 | [1-9] DIGIT*
STRING -> [_ | . | LOWERCASE | UPPERCASE] [_ | . | LOWERCASE | UPPERCASE | DIGIT]*
BOOL -> true | false
PATH -> " [/ | _ | . | LOWERCASE | UPPERCASE | DIGIT]+ "
VALUE_STRING -> " STRING "

VAR -> STRING
VAL ->
    INT
    | VALUE_STRING
    | BOOL
    | PATH
    | LIST<INT>
    | LIST<VALUE_STRING>
    | LIST<BOOL>
    
SET ->
    SET<VAL>
    | range ( INT , INT )
    
EXPR -> VAR | VAL | GRAPH

GRAPH -> VALUE_STRING
GRAPH -> set_start(SET, GRAPH)
GRAPH -> set_final(SET, GRAPH)
GRAPH -> add_start(SET, GRAPH)
GRAPH -> add_final(SET, GRAPH)
GRAPH -> load(PATH)
GRAPH -> intersect(GRAPH, GRAPH)
GRAPH -> concat(GRAPH, GRAPH)
GRAPH -> union(GRAPH, GRAPH)
GRAPH -> kleen_star(GRAPH, GRAPH)

EXPR -> VERTEX | VERTICES
VERTEX -> INT
VERTICES -> SET<VERTEX> | range ( INT , INT )
VERTICES -> get_start(GRAPH)
VERTICES -> get_final(SET, GRAPH)

EXPR -> PAIR_OF_VERTICES
PAIR_OF_VERTICES -> SET<(INT, INT)>
PAIR_OF_VERTICES -> get_reachable(GRAPH)

VERTICES -> get_vertices(GRAPH)

EXPR -> EDGE | EDGES
EDGE -> (INT, VALUE_STRING, INT) | (INT, INT, INT)
EDGES -> SET<EDGE>
EDGES -> get_edges(GRAPH)

EXPR -> LABELS
LABELS -> SET<INT> | SET<VALUE_STRING>
LABELS -> get_labels(GRAPH)

EXPR -> map(LAMBDA, EXPR)
EXPR -> filter(LAMBDA, EXPR)

LAMBDA -> (LIST<VAR> -> [BOOL_EXPR | EXPR])
BOOL_EXPR ->
    BOOL_EXPR or BOOL_EXPR
    | BOOL_EXPR and BOOL_EXPR
    | not BOOL_EXPR
    | BOOL
    | has_label(EDGE, VALUE_STRING)
    | is_start(VERTEX)
    | is_final(VERTEX)
    | X in SET<X>

LIST<X> -> list(X [, X]*) | list()
SET<X> -> set(X [, X]*) | set()
```

### Пример программы
Данный скрипт загружает граф "go", задает стартовые и финальные вершины, создает запрос, выполняет пересечение и печатает результат.
```
graph = load("go")
h = set_start(set_final(get_vertices(graph), graph)), range(1, 10))
l = union("l1", "l2")
query = kleen_star(union("type", l))
res = intersect(graph, query)
print(res)
```


## Правила вывода типов

Константы типизируются очевидным образом.

Тип переменной определяется типом выражения, с которым она связана.
```
[b(v)] => t
_________________
[Var (v)](b) => t
```

Загрузить можно только автомат.
```
_________________________
[Load (p)](b) => FA<int>
```

Установка финальных состояний, а так же добавление стартовых и финальных типизируется аналогично типизации установки стартовых, которая приведена ниже.
```
[s](b) => Set<t> ;  [e](b) => FA<t>
___________________________________
[Set_start (s, e)](b) => FA<t>
[s](b) => Set<t> ;  [e](b) => RSM<t>
____________________________________
[Set_start (s, e)](b) => RSM<t>
```

Получение финальных типизируется аналогично получению стартовых, правила для которого приведены ниже.
```
[e](b) => FA<t>
____________________________
[Get_start (e)](b) => Set<t>
[e](b) => RSM<t>
____________________________
[Get_start (e)](b) => RSM<t>
```

```
[e](b) => FA<t>
__________________________________
[Get_reachable (e)](b) => Set<t*t>
[e](b) => RSM<t>
__________________________________
[Get_reachable (e)](b) => Set<t*t>
```

```
[e](b) => FA<t>
_______________________________
[Get_vertices (e)](b) => Set<t>
[e](b) => RSM<t>
_______________________________
[Get_vertices (e)](b) => Set<t>
[e](b) => FA<t>
______________________________________
[Get_edges (e)](b) => Set<t*string*t>
[e](b) => RSM<t>
______________________________________
[Get_edges (e)](b) => Set<t*string*t>
[e](b) => FA<t>
__________________________________
[Get_labels (e)](b) => Set<string>
[e](b) => RSM<t>
__________________________________
[Get_labels (e)](b) => Set<string>
```

Правила для ```map``` и ```filter``` традиционные.
```
[f](b) => t1 -> t2 ; [q](b) => Set<t1>
_______________________________________
[Map (f,q)](b) => Set<t2>
[f](b) => t1 -> bool ; [q](b) => Set<t1>
________________________________________
[Filter (f,q)](b) => Set<t1>
```

Пересечение для двух КС не определено.
```
[e1](b) => FA<t1> ;  [e2](b) => FA<t2>
______________________________________
[Intersect (e1, e2)](b) => FA<t1*t2>
[e1](b) => FA<t1> ;  [e2](b) => RSM<t2>
_______________________________________
[Intersect (e1, e2)](b) => RSM<t1*t2>
[e1](b) => RSM<t1> ;  [e2](b) => FA<t2>
_______________________________________
[Intersect (e1, e2)](b) => RSM<t1*t2>
```

Остальные операции над автоматами типизируются согласно формальных свойств классов языков.
```
[e1](b) => FA<t> ;  [e2](b) => FA<t>
_____________________________________
[Concat (e1, e2)](b) => FA<t>
[e1](b) => FA<t> ;  [e2](b) => RSM<t>
______________________________________
[Concat (e1, e2)](b) => RSM<t>
[e1](b) => RSM<t> ;  [e2](b) => FA<t>
______________________________________
[Concat (e1, e2)](b) => RSM<t>
[e1](b) => RSM<t> ;  [e2](b) => RSM<t>
______________________________________
[Concat (e1, e2)](b) => RSM<t>
```

```
[e1](b) => FA<t> ;  [e2](b) => FA<t>
______________________________________
[Union (e1, e2)](b) => FA<t>
[e1](b) => FA<t> ;  [e2](b) => RSM<t>
_______________________________________
[Union (e1, e2)](b) => RSM<t>
[e1](b) => RSM<t> ;  [e2](b) => FA<t>
_______________________________________
[Union (e1, e2)](b) => RSM<t>
[e1](b) => RSM<t> ;  [e2](b) => RSM<t>
_______________________________________
[Union (e1, e2)](b) => RSM<t>
```

```
[e](b) => FA<t>
______________________
[Star (e)](b) => FA<t>
[e](b) => RSM<t>
______________________
[Star (e](b) => RSM<t>
```

```
[e](b) => string
________________________
[Smb (e)](b) => FA<int>
```


## Динамическая семантика языка запросов

Связывание переопределяет имя.

```
[e](b1) => x,b2
_____________________________________
[Bind (v, e)](b1) => (), (b1(v) <= x)
```

Загрузить можно только автомат и у него все вершины будут стартовыми и финальными.

```
[p](b1) => s,b2 ; read_fa_from_file s => fa
_____________________________________
[Load (p)](b1) => (fa | fa.start = fa.vertices, fa.final = fa.vertices), b1
```

