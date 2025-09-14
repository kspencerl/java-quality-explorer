# 📊 CK Metrics Extractor

This project automates the analysis of **Java source code metrics** using the [CK (Chidamber & Kemerer)](https://github.com/mauricioaniche/ck) tool. The application downloads a Java GitHub repository as a ZIP file, runs the CK Tool, and displays metrics by **class**, **method**, **field**, and **variable**.

---

## 🧠 What is CK?

**CK** stands for *Chidamber & Kemerer* – the authors of one of the first sets of object-oriented metrics. The **CK** tool implements and extends these metrics for Java projects. It performs static code analysis and generates `.csv` files with detailed metrics.

---

## 📈 Extracted Metrics

The script analyzes and prints the following metrics:

### class.csv

This table contains metrics extracted at the **class level**, which are fundamental for understanding the **structural design** of a system. Metrics like `cbo` (Coupling Between Objects), `rfc` (Response For a Class), `wmc` (Weighted Methods per Class), and `lcom` (Lack of Cohesion of Methods) are widely used in **object-oriented software engineering** to evaluate **coupling**, **cohesion**, **complexity**, and **size** of classes. For example, a high `cbo` value may indicate that the class is too dependent on others, making maintenance difficult. `lcom` helps identify if the class methods are well related to each other. Additionally, metrics like `loc`, `loopQty`, `assignmentsQty`, and `logStatementsQty` help estimate the size and complexity of the logic implemented in the class.

| Column                   | Description                                                               |
|--------------------------|---------------------------------------------------------------------------|
| file                     | Path of the analyzed Java file.                                          |
| class                    | Fully qualified class name.                                              |
| type                     | Class type (e.g., class, interface, enum).                              |
| cbo                      | Coupling Between Objects — coupling between objects.                     |
| cboModified              | CBO variant considering indirect calls.                                  |
| fanin                    | Number of methods that call this class.                                  |
| fanout                   | Number of methods called by this class.                                  |
| wmc                      | Weighted Methods per Class — sum of method complexities.                 |
| dit                      | Depth of Inheritance Tree — depth in inheritance hierarchy.              |
| noc                      | Number of Children — number of direct subclasses.                        |
| rfc                      | Response for a Class — number of methods that can be executed.           |
| lcom                     | Lack of Cohesion of Methods — cohesion between class methods.            |
| lcom*                    | Refined LCOM variant.                                                     |
| tcc                      | Tight Class Cohesion.                                                    |
| lcc                      | Loose Class Cohesion.                                                    |
| totalMethodsQty          | Total methods in the class.                                              |
| staticMethodsQty         | Number of static methods.                                                |
| publicMethodsQty         | Number of public methods.                                                |
| privateMethodsQty        | Number of private methods.                                               |
| protectedMethodsQty      | Number of protected methods.                                             |
| defaultMethodsQty        | Number of methods with default visibility.                               |
| visibleMethodsQty        | Externally visible methods.                                              |
| abstractMethodsQty       | Number of abstract methods.                                              |
| finalMethodsQty          | Number of final methods.                                                 |
| synchronizedMethodsQty   | Number of synchronized methods.                                          |
| totalFieldsQty           | Total attributes in the class.                                           |
| staticFieldsQty          | Number of static attributes.                                             |
| publicFieldsQty          | Public attributes.                                                       |
| privateFieldsQty         | Private attributes.                                                      |
| protectedFieldsQty       | Protected attributes.                                                    |
| defaultFieldsQty         | Attributes with default visibility.                                      |
| finalFieldsQty           | Final attributes.                                                        |
| synchronizedFieldsQty    | Synchronized attributes.                                                 |
| nosi                     | Number of Static Invocations — static calls made.                        |
| loc                      | Lines of Code — lines of code in the class.                              |
| returnQty                | Number of `return` statements.                                           |
| loopQty                  | Number of loops (for, while, etc).                                       |
| comparisonsQty           | Number of comparisons (`==`, `<`, etc).                                  |
| tryCatchQty              | Try-catch blocks.                                                        |
| parenthesizedExpsQty     | Parenthesized expressions.                                               |
| stringLiteralsQty        | String literals.                                                         |
| numbersQty               | Numeric literals.                                                        |
| assignmentsQty           | Assignments.                                                             |
| mathOperationsQty        | Mathematical operations.                                                 |
| variablesQty             | Number of variables used.                                                |
| maxNestedBlocksQty       | Maximum depth of nested blocks.                                          |
| anonymousClassesQty      | Number of anonymous classes.                                             |
| innerClassesQty          | Number of inner classes.                                                 |
| lambdasQty               | Number of lambda expressions.                                            |
| uniqueWordsQty           | Unique words used in the code.                                           |
| modifiers                | Class modifiers (e.g., public, abstract).                               |
| logStatementsQty         | Number of log calls (e.g., `logger.info()`).                            |

### method.csv

This table details metrics at the **method** level, useful for finer analysis such as identifying **complex methods**, **code smells**, and **refactoring** opportunities. Metrics like `wmc` (Weighted Method Count) and `cc` (cyclomatic complexity, when available) are essential for checking the difficulty of reading and testing the method. The number of `returnsQty`, `loopQty`, `comparisonsQty`, and `tryCatchQty` indicate the **level of branching and control flow**, which directly impacts **maintainability**. Metrics like `methodsInvokedQty` and `parametersQty` help identify **high responsibility** or **long methods** that may violate principles like **SRP (Single Responsibility Principle)**.

| Column                          | Description                                                             |
|---------------------------------|-------------------------------------------------------------------------|
| file                            | Path of the analyzed Java file.                                        |
| class                           | Class to which the method belongs.                                      |
| method                          | Method name.                                                           |
| constructor                     | Indicates if it's a constructor (`true`/`false`).                      |
| line                            | Line where the method starts.                                          |
| cbo                             | Coupling Between Objects for the method.                               |
| cboModified                     | CBO variant.                                                           |
| fanin                           | Number of methods that call this one.                                  |
| fanout                          | Number of methods called by this one.                                  |
| wmc                             | Weighted Method Count — method complexity.                             |
| rfc                             | Methods that can be executed in response to a call.                    |
| loc                             | Lines of code in the method.                                           |
| returnsQty                      | Number of `return` statements in the method.                           |
| variablesQty                    | Number of variables used.                                              |
| parametersQty                   | Number of method parameters.                                           |
| methodsInvokedQty               | Total methods invoked.                                                 |
| methodsInvokedLocalQty          | Local methods invoked.                                                 |
| methodsInvokedIndirectLocalQty  | Indirectly local methods invoked.                                      |
| loopQty                         | Loops (`for`, `while`, etc).                                          |
| comparisonsQty                  | Comparisons.                                                           |
| tryCatchQty                     | Try-catch blocks.                                                      |
| parenthesizedExpsQty            | Parenthesized expressions.                                             |
| stringLiteralsQty               | String literals.                                                       |
| numbersQty                      | Numeric literals.                                                      |
| assignmentsQty                  | Assignments.                                                           |
| mathOperationsQty               | Mathematical operations.                                               |
| maxNestedBlocksQty              | Maximum depth of nested blocks.                                        |
| anonymousClassesQty             | Anonymous classes in the method.                                       |
| innerClassesQty                 | Inner classes in the method.                                           |
| lambdasQty                      | Lambdas in the method.                                                 |
| uniqueWordsQty                  | Unique words used.                                                     |
| modifiers                       | Applied modifiers (e.g., public, static).                             |
| logStatementsQty                | Logging calls.                                                         |
| hasJavaDoc                      | Indicates if the method has Javadoc (`true`/`false`).                 |

### field.csv & variable.csv

These two tables show the usage of **variables and fields** throughout the code, detailing their presence by class and method. They are useful for identifying patterns of **excessive use of global variables**, **inadequate reuse**, or **poor encapsulation**. The `usage` metric indicates whether the variable was **read, written, or both**, helping with analyses about **immutability** or **excessive use of mutable states**. This information is valuable in code audits, searching for better encapsulation practices and clean design.

| Column    | Description                                             |
|-----------|---------------------------------------------------------|
| file      | Path of the analyzed Java file.                        |
| class     | Class where the variable or field appears.             |
| method    | Method where the variable is used (if applicable).     |
| variable  | Name of the variable or field.                         |
| usage     | Type of usage (read, write, etc).                      |

---

## 📦 Requirements

- Python 3.8+
- GitPython
- pandas
- requests
- Java JDK 17
- Apache Maven (to build the CK JAR)
- CK Tool JAR

Install Python dependencies:

```bash
pip install -r code/requirements.txt
```

---

## ⚙️ Virtual Environment

It is recommended to use a Python virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate    # Windows
```

---

## 🚀 Running the Project

### 1️⃣ Get the CK Tool JAR

The JAR already is in `code/ck/target/ck-0.7.1-SNAPSHOT-jar-with-dependencies.jar`, but you can build the JAR manually (Java 17 + Maven) if you want:

```bash
git clone https://github.com/mauricioaniche/ck.git
cd ck
mvn clean package
```

The JAR will be generated at:
`ck/target/ck-0.7.1-SNAPSHOT-jar-with-dependencies.jar`

Or download a pre-built JAR from:
https://github.com/joaopauloaramuni/laboratorio-de-experimentacao-de-software/tree/main/PROJETOS/Projeto%20CK%20Metrics%20Extractor/ck/target

---

### 2️⃣ Run the Python Script

```bash
python code/ck_metrics_extractor.py
```

Enter the GitHub repository URL when prompted, for example (whithout .git in the URL):

```
https://github.com/spring-projects/spring-petclinic
```

---

## 📄 Generated Files

After execution, the following `.csv` files will be generated in `code/ck_output/`:

- class.csv
- method.csv
- field.csv
- variable.csv

The script will print the main data from each metric table.