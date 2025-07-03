# Soorj (Սուրճ) - An Armenian Programming Language
**Soorj** is an Armenian programming language that aims to make programming more accessible to Armenian speakers by using Armenian as the written language for coding. It is a interpreted, dynamically typed, object-oriented programming language, similar to Python. The name "Soorj" means coffee in Armenian which is a play on "Java" (the author's favorite programming language). As the language is still in development, it remains feature-incomplete.

## Features

- **Armenian Keywords**: Uses Armenian (yes, Armenian characters) words for programming constructs
- **Easy to Learn**: Simple syntax similar to other modern programming languages (very similar to Python)
- **Interactive REPL**: Test code instantly with the built-in Read-Eval-Print Loop
- **File Execution**: Run complete programs from `.soorj` files
- **Built-in Functions**: Includes some useful functions with Armenian names

## Installation

For now, no installation required! Just make sure you have Python 3.7+ installed:

```bash
python3 --version  # Should show 3.7 or higher
```

Your program will be 

## Usage

### Interactive Mode (REPL)

Start the interactive shell:

```bash
python3 soorj.py
```

Now let's run our first simple program!

```soorj
գրէ("Բարեւ աշխարգ!")

"Բարեւ աշխարգ!"
```

### Running `.soorj` Files

Create a `.soorj` file and run it:

```bash
❯ python3 soorj.py example.soorj
Բարեւ աշխարգ!
Գումարը: 30.0
Այո
1.0
2.0
3.0
2-ի 3-րդ աստիճանը: 8.0
```

## Armenian Keywords

| Soorj Keyword (Armenian Script) | Armenian (Transliterated) | English Meaning | Python Equivalent |
|---------|---------------------------|-----------------|-----------------|
| `եթե` | yete | if | `if` |
| `հպ` short for `հակառակ պարագային` | hagarak baragayin | otherwise | `else` |
| `մինչև` | minchev | until | `while` |
| `գործ` | kordz | work | `def` (for defining functions) |
| `տուր` | dur | give | `return` |
| `այո` | ayo | yes | `True` |
| `ոչ` | voch | no | `False` |
| `հեչ` | hech | nothing | `None` |
| `և` | yev | and | `and` |
| `կամ` | gam | or | `or` |
| `չի` | chi | not | `not` |

## Built-in Functions

- `գրէ(...)` - (kre/write) Print values to console
- `թիվ(x)` - (tiv/number) Converts value to number
- `բառ(x)` - (par/word) Converts value to string

## Grammar

The language supports:

- **Variables/Function Names (with Armenian characters)**: `ա = 5`
- **Blocks**: `{ ... }`
- **Assignments**: `ա = 5`
- **Function Definitions**: `գործ աստիճան(ա, բ) { ... }`
- **Function Calls**: `աստիճան(2, 3)`
- **Arithmetic**: `+`, `-`, `*`, `/`, `%`
- **Boolean Comparison**: `==`, `!=`, `<`, `>`, `<=`, `>=`
- **Logical Operators**: `yev` (and), `gam` (or), `chi` (not)
- **Strings (with Armenian characters)**: `"Բարեւ"`, `'Աշխարհ'`
- **Numbers**: `42`, `3.14`
- **Booleans**: `այո` (yes), `ոչ` (no)
- **Null**: `հեչ` (nothing)
- **Comments**: `# ասի նշում է` (literally: "this is a note")

## Language Examples

### Basic Variables and Arithmetic

```soorj
ա = 10
բ = 20
գ = ա + բ
գրէ(գ) # 30
```

### Conditional Statements

```soorj
ա = 10
եթե ա > 5 {
    գրէ("Այո")
} հպ {
    գրէ("Ոչ")
}

# "Այո"
```

### Loops

```soorj
ա = 1
մինչև ա <= 3 {
    գրէ(ա)
    ա = ա + 1
}

# 1
# 2
# 3
```

### Define and Call Functions

```soorj
գործ բաու(ա, բ) {
    եթե բ == 0 {
        տուր 1
    }
    պատասխան = ա
    գ = 1
    մինչև գ < բ {
        պատասխան = (պատասխան * ա)
        գ = գ + 1
    }
    տուր պատասխան
}

ա = բաու(2, 3)
գրէ(ա) # 8
```

### Type Conversion

```soorj
ա = "10.5"
բ = թիվ(ա)
գրէ(բ) # 10.5
```

### Boolean Operations

```soorj
ա = այո
բ = ոչ
գրէ(ա և բ) # ոչ
գրէ(ա կամ բ) # այո
գրէ(ա չի) # ոչ
```

## Future Enhancements

- range operators
- error handling
- class and object support

## Contributing

This is an experimental language created to explore programming concepts using the Armenian language. Contributions are welcome!

## License

See LICENSE file for details.

---

Ուրախ օրեր և բարի հաջողութիւն! (Literally: "Happy days and good luck!") 🇦🇲
