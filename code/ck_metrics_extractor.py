import os
import shutil
import subprocess
import sys
import pandas as pd
from git import Repo

def clone_repo(repo_url, dest_dir='repo'):
    """
    Downloads and extracts the GitHub repository as ZIP to a local directory.
    If the directory already exists, it will be removed before downloading again.
    """
    import requests
    import zipfile
    from io import BytesIO

    if os.path.exists(dest_dir):
        shutil.rmtree(dest_dir)

    print(f"[+] Preparing ZIP download from {repo_url} ...")
    # Extract owner and repo from URL
    url_parts = repo_url.rstrip('/').split('/')
    repo_owner = url_parts[-2]
    repo_name = url_parts[-1]
    api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}"
    r = requests.get(api_url)
    if r.status_code == 200:
        default_branch = r.json().get("default_branch", "main")
    else:
        default_branch = "main"

    zip_url = f"https://github.com/{repo_owner}/{repo_name}/archive/refs/heads/{default_branch}.zip"

    print(f"[+] Downloading ZIP: {zip_url}")
    response = requests.get(zip_url)
    if response.status_code != 200:
        print(f"Error downloading ZIP: {zip_url}")
        sys.exit(1)

    with zipfile.ZipFile(BytesIO(response.content)) as zip_ref:
        zip_ref.extractall(dest_dir)

    extracted_dir = os.path.join(dest_dir, f"{repo_name}-{default_branch}")
    if not os.path.exists(extracted_dir):
        print(f"Error: extracted directory not found: {extracted_dir}")
        sys.exit(1)
    return extracted_dir

def run_ck(jar_path, repo_dir, output_dir=None):
    """
    Executes the CK Tool and returns paths to the generated .csv files.
    """
    # Create a unique directory for each repository if not specified
    if output_dir is None:
        import time
        timestamp = int(time.time())
        output_dir = f'ck_output_{timestamp}'
    
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)

    print(f"[+] Running CK Tool on sources in {repo_dir} ...")
    print(f"[+] Saving results to {output_dir} ...")
    
    cmd = [
        'java', '-jar', jar_path,
        repo_dir,
        'true',      # use JARs
        '0',         # max files per partition = automatic
        'false',     # DO NOT extract variable and field metrics (classes only)
        output_dir + os.sep
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing CK: {e}")
        print(f"Stderr: {e.stderr}")
        return None

    # Paths to generated files
    files = {
        'class': os.path.join(output_dir, 'class.csv'),
        'field': os.path.join(output_dir, 'field.csv'),
        'method': os.path.join(output_dir, 'method.csv'),
        'variable': os.path.join(output_dir, 'variable.csv'),
    }

    # Confirm if class.csv exists
    if not os.path.exists(files['class']):
        print(f"Error: class.csv not found in {output_dir}")
        return None

    return files

def aggregate_metrics_by_repo(df_class, repo_name):
    """
    Aggregates CBO, DIT and LCOM metrics by repository.
    Calculates descriptive statistics for each metric.
    """
    metrics = ['cbo', 'dit', 'lcom']
    available_metrics = [metric for metric in metrics if metric in df_class.columns]
    
    if not available_metrics:
        print(f"[!] No metrics found for {repo_name}")
        return None
    
    # Calculate statistics for each metric
    repo_stats = {'repo': repo_name, 'total_classes': len(df_class)}
    
    for metric in available_metrics:
        # Remove NaN/null values for calculations
        metric_values = df_class[metric].dropna()
        
        if len(metric_values) > 0:
            repo_stats.update({
                f'{metric}_mean': round(metric_values.mean(), 3),
                f'{metric}_median': round(metric_values.median(), 3),
                f'{metric}_std': round(metric_values.std(), 3),
                f'{metric}_min': metric_values.min(),
                f'{metric}_max': metric_values.max(),
                f'{metric}_q1': round(metric_values.quantile(0.25), 3),
                f'{metric}_q3': round(metric_values.quantile(0.75), 3)
            })
        else:
            # Default values if no valid data
            for stat in ['mean', 'median', 'std', 'min', 'max', 'q1', 'q3']:
                repo_stats[f'{metric}_{stat}'] = None
    
    return repo_stats


def load_and_print_class_metrics(class_csv_path):
    """
    Loads class metrics from CSV, selects only CBO, DIT and LCOM and prints the first lines.
    """
    print("\n[+] Reading CLASS metrics (CBO, DIT, LCOM) ...")
    df_class = pd.read_csv(class_csv_path)

    # Required columns: identification + CBO, DIT and LCOM metrics
    class_columns = [
        'file', 'class', 'type',
        'cbo',   # Coupling Between Objects
        'dit',   # Depth of Inheritance Tree
        'lcom',  # Lack of Cohesion of Methods
    ]

    available_class_cols = [col for col in class_columns if col in df_class.columns]
    print(f"Available metrics: {available_class_cols}")
    print(df_class[available_class_cols].head())  # Show first 5 lines


def process_multiple_repos(repo_list_csv, ck_jar_path, output_csv="all_class_metrics.csv"):
    """
    Processes multiple repositories and extracts only CBO, DIT and LCOM metrics.
    Saves the result in a single consolidated CSV.
    """
    df_all = []

    repos = pd.read_csv(repo_list_csv)
    for i, row in repos.iterrows():
        repo_url = row["url"]
        print(f"\n=== [{i+1}/{len(repos)}] Processing {repo_url} ===")
        try:
            repo_path = clone_repo(repo_url)
            csv_paths = run_ck(ck_jar_path, repo_path)

            # Load class metrics and filter only required columns
            df_class = pd.read_csv(csv_paths["class"])
            
            # Select only identification columns and CBO, DIT and LCOM metrics
            required_columns = ['file', 'class', 'type', 'cbo', 'dit', 'lcom']
            available_columns = [col for col in required_columns if col in df_class.columns]
            
            df_filtered = df_class[available_columns].copy()
            df_filtered["repo"] = f"{row['owner']}/{row['name']}"
            df_all.append(df_filtered)
            
            print(f"[+] Extracted {len(df_filtered)} classes with CBO, DIT and LCOM metrics")
            
        except Exception as e:
            print(f"[!] Failed on {repo_url}: {e}")
            continue

    # Consolidate everything
    if df_all:
        df_final = pd.concat(df_all, ignore_index=True)
        df_final.to_csv(output_csv, index=False)
        print(f"\n[✓] File saved in {output_csv} with {len(df_final)} lines containing CBO, DIT and LCOM metrics.")
    else:
        print("[!] No data was processed successfully.")


def process_multiple_repos_aggregated(repo_list_csv, ck_jar_path, output_csv="aggregated_repo_metrics.csv"):
    """
    Processes multiple repositories and aggregates CBO, DIT and LCOM metrics by repository.
    Saves aggregated statistics (mean, median, etc.) in a consolidated CSV.
    """
    repo_aggregated_data = []

    repos = pd.read_csv(repo_list_csv)
    for i, row in repos.iterrows():
        repo_url = row["url"]
        repo_name = f"{row['owner']}/{row['name']}"
        print(f"\n=== [{i+1}/{len(repos)}] Processing {repo_url} ===")
        
        try:
            repo_path = clone_repo(repo_url)
            csv_paths = run_ck(ck_jar_path, repo_path)
            
            # Check if CK was executed successfully
            if csv_paths is None:
                print(f"[!] CK Tool failed for {repo_name}")
                continue
                
            # Check if class.csv file exists and has content
            if not os.path.exists(csv_paths["class"]):
                print(f"[!] class.csv not found for {repo_name}")
                continue

            # Load class metrics
            df_class = pd.read_csv(csv_paths["class"])
            print(f"[+] Loaded {len(df_class)} classes from {repo_name}")
            
            # If there are no Java classes, skip the repository
            if len(df_class) == 0:
                print(f"[!] No Java classes found in {repo_name}")
                continue
            
            # Aggregate metrics by repository
            repo_stats = aggregate_metrics_by_repo(df_class, repo_name)
            
            if repo_stats:
                repo_aggregated_data.append(repo_stats)
                print(f"[+] Aggregated metrics for {repo_name}: {repo_stats['total_classes']} classes")
                
                # Save data progressively to avoid loss in case of interruption
                if len(repo_aggregated_data) % 10 == 0:  # Every 10 repositories
                    df_temp = pd.DataFrame(repo_aggregated_data)
                    df_temp.to_csv(f"temp_{output_csv}", index=False)
                    print(f"[📁] Temporary backup saved with {len(repo_aggregated_data)} repositories")
            
        except Exception as e:
            print(f"[!] Failed on {repo_url}: {e}")
            continue
        
        # Cleanup: remove temporary directories
        try:
            if 'repo_path' in locals():
                parent_dir = os.path.dirname(repo_path)
                if os.path.exists(parent_dir):
                    shutil.rmtree(parent_dir)
            if 'csv_paths' in locals() and csv_paths:
                output_dir = os.path.dirname(csv_paths["class"])
                if os.path.exists(output_dir):
                    shutil.rmtree(output_dir)
        except:
            pass  # Ignore cleanup errors

    # Save final aggregated data
    if repo_aggregated_data:
        df_aggregated = pd.DataFrame(repo_aggregated_data)
        df_aggregated.to_csv(output_csv, index=False)
        print(f"\n[✓] Aggregated metrics saved in {output_csv} with {len(df_aggregated)} repositories.")
        
        # Show statistics preview
        print(f"\n[📊] Preview of aggregated metrics:")
        display_cols = ['repo', 'total_classes']
        for metric in ['cbo', 'dit', 'lcom']:
            if f'{metric}_mean' in df_aggregated.columns:
                display_cols.append(f'{metric}_mean')
        print(df_aggregated[display_cols].head())
        
        # Remove temporary file if it exists
        temp_file = f"temp_{output_csv}"
        if os.path.exists(temp_file):
            os.remove(temp_file)
        
    else:
        print("[!] No aggregated data was generated.")


def main():
    print("== CK Metrics Extractor - CBO, DIT and LCOM Metrics ==")
    
    # Processing options
    print("\n1. Process multiple repositories - CLASS-level metrics")
    print("2. Process multiple repositories - AGGREGATED metrics by repository")
    print("3. Process a single repository")
    choice = input("Choose an option (1, 2 or 3): ").strip()
    
    ck_jar_path = os.path.join("ck", "target", "ck-0.7.1-SNAPSHOT-jar-with-dependencies.jar")
    
    if not os.path.exists(ck_jar_path):
        print(f"Error: {ck_jar_path} not found.")
        print("Run the commands in README to download and compile the CK Tool.")
        sys.exit(1)
    
    if choice in ["1", "2"]:
        # Process multiple repositories
        csv_file = input("Enter the path to the CSV file with repositories (ex: repositories.csv): ").strip()
        if not os.path.exists(csv_file):
            print(f"Error: file {csv_file} not found.")
            sys.exit(1)
        
        if choice == "1":
            # Class-level metrics
            output_file = input("Output file name (default: all_class_metrics.csv): ").strip()
            if not output_file:
                output_file = "all_class_metrics.csv"
            
            print(f"\n[+] Processing repositories (class-level metrics) from file {csv_file}...")
            process_multiple_repos(csv_file, ck_jar_path, output_file)
            
        elif choice == "2":
            # Aggregated metrics by repository
            output_file = input("Output file name (default: aggregated_repo_metrics.csv): ").strip()
            if not output_file:
                output_file = "aggregated_repo_metrics.csv"
            
            print(f"\n[+] Processing repositories (aggregated metrics) from file {csv_file}...")
            process_multiple_repos_aggregated(csv_file, ck_jar_path, output_file)
        
    elif choice == "3":
        # Process a single repository (simplified original mode)
        repo_url = input("Enter the GitHub repository URL: ").strip()
        
        # Clone repository and run CK
        repo_path = clone_repo(repo_url)
        csv_paths = run_ck(ck_jar_path, repo_path)
        
        # Process only class metrics with CBO, DIT and LCOM
        load_and_print_class_metrics(csv_paths['class'])
        
    else:
        print("Invalid option.")
        sys.exit(1)

if __name__ == "__main__":
    main()

# Download the CK Tool and build the JAR file (ck/target/ck-0.7.1-SNAPSHOT-jar-with-dependencies.jar):
# git clone https://github.com/mauricioaniche/ck.git
# cd ck
# mvn clean package
# Documentation: https://github.com/mauricioaniche/ck

# Install the necessary dependencies for this project:
# pip install gitpython pandas requests

# Run the script:
# python ck_metrics_extractor.py

# Example repositories:
# - Single: https://github.com/spring-projects/spring-petclinic
# - Multiple: use repositories.csv with columns: url, owner, name

# Output options:
# 1. CLASS-level metrics: CSV with one line per class (all_class_metrics.csv)
# 2. AGGREGATED metrics: CSV with one line per repository with statistics (aggregated_repo_metrics.csv)
#    - Includes: mean, median, standard deviation, min, max, quartiles for each metric

# Extracted metrics (only):
# - CBO: Coupling Between Objects
# - DIT: Depth of Inheritance Tree
# - LCOM: Lack of Cohesion of Methods