# Arabx Compiler

Arabx lets you write and compile programs using Arabic keywords. Source files use the `.arabx` extension.


## Usage

```bash
python src/arabx.py <file.arabx>
```


## Data Types

| Keyword | Type |
|---|---|
| `sahih` | Integer |
| `ashri` | Float |
| `nass` | String |
| `mantqi` | Boolean |


## Variables

```
mutghyr <name>: <type> = <value>;
```

```
mutghyr age: sahih = 25;
mutghyr pi: ashri = 3.14;
mutghyr name: nass = "Ahmad";
mutghyr passed: mantqi = sawab;
```

To reassign a variable:
```
<name> = <value>;
```


## Operators

**Arithmetic:** `+` `-` `*` `/` `%`

**Comparison:** `==` `!=` `<` `>` `<=` `>=`

**Logical:** `wa` (AND), `aw` (OR), `lays` (NOT)


## If / Else

```
idha (<condition>) {
    ...
} wala {
    ...
}
```


## While Loop

talama (<condition>) {
    ...
}
```


## Functions

```
dalah <name>(<param>: <type>): <return_type> {
    irjaa <value>;
}
```

## Print

```
utbaa(<value>);
```

## Full Examples

See the [`examples/`](./examples) folder:

- `examples/example1.arabx` — Variables and arithmetic
- `examples/example2.arabx` — Functions and conditions
- `examples/example3.arabx` — While loop


## Reserved Keywords

| Keyword | Meaning |
|---|---|
| `mutghyr` | متغير  |
| `sahih` | صحيح  |
| `ashri` | عشري |
| `nass` | نص  |
| `mantqi` | منطقي  |
| `sawab` | صواب  |
| `khata` | خطأ  |
| `idha` | اذا  |
| `wala` | والا  |
| `talama` | طالما  |
| `utbaa` | اطبع  |
| `dalah` | دالة |
| `irjaa` | ارجع  |
| `wa` | و  |
| `aw` | او  |
| `lays` | ليس  |
