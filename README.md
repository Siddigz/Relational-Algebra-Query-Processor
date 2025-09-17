# Relational-Algebra-Query-Processor

3005 bonus assignment  
CLI program for processing relational algebra queries.

---

## Features

This program supports the following relational algebra operations:

- **Selection (σ)**: Filter rows based on a condition.
- **Projection (π)**: Select specific columns from a relation.
- **Join (⋈)**: Combine rows from two relations based on a related column.
- **Union (⋃)**: Combine all rows from two relations, removing duplicates.
- **Intersection (∩)**: Return rows present in both relations.
- **Difference (−)**: Return rows from the first relation not present in the second.

---

## Usage and Commands

The CLI accepts commands to process relational algebra queries on your input data. Key features and commands include:

- **Query:**  
    Enter a relational algebra expression to be processed.  
    Example:  
    ```
    Query: project SID, Name (select Age = 50 (Students))
    ```

- **select**  
    Filter rows based on a condition.  
    Example:  
    ```
    Query: select Name = 'Siddig' (Students_3)
    ```

- **project**  
    Select specific columns from a relation.  
    Example:  
    ```
    Query: project Name (select GPA > 10.5 (Students_3))
    ```

- **join**  
    Combine rows from two relations based on a common column.  
    Example:  
    ```
    Query: Students_3 join Students2 on GPA > 10.8
    ```

- **union**  
    Combine all rows from two relations, removing duplicates.  
    Example:  
    ```
    Query: Students_3 union Students2
    ```

- **intersection**  
    Return rows present in both relations.  
    Example:  
    ```
    Query: Students_3 intersection Students2
    ```

- **difference**  
    Return rows from the first relation not present in the second.  
    Example:  
    ```
    Query: Students_3 difference Students2
    ```

- **Input/Output:**  
    - Input file: Define your relations and queries.
    - Output file: Results are written here after processing.

Refer to the examples above to construct your queries in the CLI.

## Running the Program

1. **Fill the input file**  
     Prepare your input file with the required relations and queries.

2. **Run the program**
     ```bash
     python app.py
     ```

3. **Open the output file**  
     View the results in the output file.

---

## Notes

- Ensure your input file is formatted correctly.
