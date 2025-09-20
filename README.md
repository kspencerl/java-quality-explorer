# 📊 CK Metrics Extractor

This project automates the analysis of **Java source code quality metrics** using the [CK (Chidamber & Kemerer)](https://github.com/mauricioaniche/ck) tool. The application downloads Java GitHub repositories as ZIP files, runs the CK Tool, and extracts **CBO**, **DIT**, and **LCOM** metrics for quality analysis.

The tool supports three processing modes:
1. **Multiple repositories - Class-level metrics**: Detailed CSV with one row per class
2. **Multiple repositories - Aggregated metrics**: Summary CSV with statistical metrics per repository  
3. **Single repository analysis**: Interactive analysis for testing and exploration

---

## 🎯 Focus Metrics

This tool specifically extracts three key object-oriented design quality metrics:

- **CBO (Coupling Between Objects)**: Measures dependencies between classes
- **DIT (Depth of Inheritance Tree)**: Measures inheritance hierarchy depth  
- **LCOM (Lack of Cohesion of Methods)**: Measures class cohesion quality

These metrics are essential for evaluating **code maintainability**, **design quality**, and **technical debt** in large-scale Java projects.

---

## 🧠 What is CK?

**CK** stands for *Chidamber & Kemerer* – the authors of one of the first sets of object-oriented metrics. The **CK** tool implements and extends these metrics for Java projects. It performs static code analysis and generates `.csv` files with detailed metrics.

---

## 📈 Processing Options

### 1. Multiple Repositories - Class-level Metrics
- Processes multiple repositories from a CSV file
- Generates detailed metrics for **each individual class**
- Output: `all_class_metrics.csv` with one row per class
- Ideal for: Detailed analysis, machine learning datasets, class-level studies

### 2. Multiple Repositories - Aggregated Metrics ⭐ **Recommended**
- Processes multiple repositories from a CSV file  
- Generates **statistical summaries per repository**
- Calculates: mean, median, std dev, min, max, quartiles for each metric
- Output: `aggregated_repo_metrics.csv` with one row per repository
- Ideal for: Repository comparison, quality benchmarking, large-scale analysis

### 3. Single Repository Analysis
- Interactive analysis of a single GitHub repository
- Generates CSV files in unique timestamped directory (e.g., `ck_output_1234567890/`)
- Displays metrics summary in terminal
- Ideal for: Testing, exploration, quick analysis of individual projects

---

## 📊 Key Metrics Explained

### CBO (Coupling Between Objects)
- **Range**: 0 to N (higher = more coupled)
- **Good**: Low values (0-5)
- **Bad**: High values (>10)
- **Impact**: High coupling makes code harder to maintain and test

### DIT (Depth of Inheritance Tree)  
- **Range**: 0 to N (higher = deeper inheritance)
- **Good**: Moderate values (1-4)
- **Bad**: Very deep (>6) or very shallow (0) hierarchies
- **Impact**: Affects code reusability and complexity

### LCOM (Lack of Cohesion of Methods)
- **Range**: 0.0 to 1.0 (higher = less cohesive)  
- **Good**: Low values (0.0-0.3)
- **Bad**: High values (>0.7)
- **Impact**: Low cohesion indicates classes doing too many things

---

## 📋 CSV Output Formats

### Class-level CSV (`all_class_metrics.csv`)
```csv
file,class,type,cbo,dit,lcom,repo
src/main/App.java,App,class,3,1,0.2,owner/repository
src/util/Helper.java,Helper,class,7,2,0.8,owner/repository
```

### Aggregated CSV (`aggregated_repo_metrics.csv`)  
```csv
repo,total_classes,cbo_mean,cbo_median,cbo_std,cbo_min,cbo_max,dit_mean,lcom_mean
owner/repo1,150,4.2,3.0,2.1,0,15,1.8,0.45
owner/repo2,89,5.8,4.0,3.5,0,28,2.1,0.52
```

---

## 🧠 About CK Tool

**CK** stands for *Chidamber & Kemerer* – the authors of seminal object-oriented metrics. The [CK tool](https://github.com/mauricioaniche/ck) implements and extends these metrics for Java projects through static code analysis.

### Why These Metrics Matter

- **CBO**: High coupling indicates classes that are difficult to maintain and test independently
- **DIT**: Optimal inheritance depth balances code reuse with complexity
- **LCOM**: Low cohesion suggests classes with too many responsibilities

### Research Applications

These metrics are widely used in software engineering research for:
- **Code quality assessment**
- **Technical debt measurement**  
- **Refactoring prioritization**
- **Design pattern analysis**
- **Evolution analysis**

---

## 📚 References

- [CK Tool Repository](https://github.com/mauricioaniche/ck)
- [Chidamber & Kemerer Metrics Suite](https://ieeexplore.ieee.org/document/295895)
- [Object-Oriented Metrics in Practice](https://link.springer.com/book/10.1007/3-540-39538-5)

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with multiple repositories
5. Submit a pull request

---

## 📄 License

This project is open source. The CK tool has its own license terms.

---

## 📦 Requirements

- Python 3.8+
- Java JDK 17+
- Internet connection (for downloading repositories)

### Python Dependencies
Install required packages:

```bash
pip install -r code/requirements.txt
```

Required packages:
- `pandas` - Data manipulation and CSV handling
- `requests` - HTTP requests for GitHub API and ZIP downloads  
- `gitpython` - Git repository operations (optional)

### Repository List Format
For multiple repository processing, create a CSV file with columns:
```csv
name,owner,url,stars,createdAt,updatedAt
spring-petclinic,spring-projects,https://github.com/spring-projects/spring-petclinic,7900,2013-01-11T17:38:31Z,2024-12-04T14:39:32Z
```

Required columns: `name`, `owner`, `url`

---

## 🚀 Quick Start

### 1️⃣ Setup Environment

```bash
cd code
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate    # Windows
pip install -r requirements.txt
```

### 2️⃣ Run the Tool

```bash
python ck_metrics_extractor.py
```

### 3️⃣ Choose Processing Option

```
== CK Metrics Extractor - Métricas CBO, DIT e LCOM ==

1. Processar múltiplos repositórios - métricas por CLASSE
2. Processar múltiplos repositórios - métricas AGREGADAS por repositório
3. Processar um único repositório
Escolha uma opção (1, 2 ou 3): 2
```

### 4️⃣ Provide Input

- **Option 1 & 2**: Provide path to CSV file with repository list
- **Option 3**: Provide single GitHub repository URL

### 5️⃣ Results

- **Option 1**: Generates `all_class_metrics.csv` 
- **Option 2**: Generates `aggregated_repo_metrics.csv`
- **Option 3**: Generates CSV files in timestamped directory + displays summary in terminal

---

## 📊 Example Usage

### Large-Scale Repository Analysis

For analyzing 1000+ repositories:

```bash
python ck_metrics_extractor.py
# Choose option 2 (aggregated metrics)
# Provide: repositories.csv
# Output: aggregated_repo_metrics.csv
```

### Single Repository Testing

For quick analysis:

```bash
python ck_metrics_extractor.py  
# Choose option 3
# Provide: https://github.com/spring-projects/spring-petclinic
# Output: CSV files in ck_output_<timestamp>/ directory + terminal summary
```

---

## Technical Details

### CK Tool Integration
- Uses pre-built CK JAR: `ck/target/ck-0.7.1-SNAPSHOT-jar-with-dependencies.jar`
- Configured to extract only class-level metrics (no field/method/variable analysis)
- Creates unique output directories per repository to avoid data conflicts

### Processing Features
- **Automatic cleanup**: Removes temporary files after processing
- **Progressive saving**: Creates backups every 10 repositories  
- **Error handling**: Skips repositories without Java code
- **Memory efficient**: Processes one repository at a time

### Performance Considerations
- Downloads repositories as ZIP (faster than git clone)
- Uses unique temporary directories (parallel processing safe)
- Automatic cleanup prevents disk space issues
- Progress tracking and error logging