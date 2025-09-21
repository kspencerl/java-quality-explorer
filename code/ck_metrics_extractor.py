import os
import shutil
import subprocess
import sys
import time
import pandas as pd


# Helpers

def _is_windows():
    return os.name == "nt"

def _run(cmd, cwd=None, timeout=None):
    return subprocess.run(
        cmd, cwd=cwd, check=True, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout
    )

def _safe_rmtree(path):
    try:
        if os.path.exists(path):
            shutil.rmtree(path, ignore_errors=True)
    except Exception:
        pass

def clone_repo(repo_url, dest_dir='repo'):
    url_parts = repo_url.rstrip('/').split('/')
    repo_owner = url_parts[-2]
    repo_name = url_parts[-1]

    # Clonaremos em dest_dir/<owner>__<name>
    repo_parent = dest_dir
    repo_path = os.path.join(repo_parent, f"{repo_owner}__{repo_name}")

    # Limpa diretório anterior
    _safe_rmtree(repo_path)
    os.makedirs(repo_parent, exist_ok=True)

    attempt = 0
    while True:
        attempt += 1
        print(f"[+] Clonando (git) {repo_url} → {repo_path} (tentativa {attempt})")
        try:
            _run(["git", "clone", "--depth", "1", "--no-tags", "--filter=blob:none", repo_url, repo_path])
            if _is_windows():
                try:
                    _run(["git", "config", "core.longpaths", "true"], cwd=repo_path)
                except subprocess.CalledProcessError:
                    pass
            break
        except subprocess.CalledProcessError as e:
            print(f"[git] Falha ao clonar: {e.stderr.strip()}")
            _safe_rmtree(repo_path)
            if attempt >= 2:
                raise
            time.sleep(2 * attempt)

    if not os.path.exists(repo_path):
        print(f"Error: diretório do repositório não encontrado: {repo_path}")
        sys.exit(1)
    return repo_path


def run_ck(jar_path, repo_dir, output_dir=None):
    """
    Executa o CK e retorna paths dos csvs.
    Se falhar com useJars=true, tenta fallback com useJars=false.
    """
    # Cria diretório único para cada execução se não especificado
    if output_dir is None:
        timestamp = int(time.time())
        output_dir = f'ck_output_{timestamp}'
    if os.path.exists(output_dir):
        _safe_rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    def _call(use_jars: bool):
        print(f"[+] Running CK Tool on sources in {repo_dir} ...")
        print(f"[+] Saving results to {output_dir} ...")
        cmd = [
            'java', '-Xms512m', '-Xmx4096m',
            '-jar', jar_path,
            repo_dir,
            'true' if use_jars else 'false',   # use JARs
            '0',                                # auto partition
            'false',                            # NÃO extrair variable/field
            output_dir + os.sep
        ]
        try:
            res = _run(cmd, timeout=3600)
            tail_err = "\n".join([ln for ln in res.stderr.splitlines() if ("WARN" in ln or "ERROR" in ln)][-50:])
            if tail_err:
                print(tail_err)
            files = {
                'class': os.path.join(output_dir, 'class.csv'),
                'field': os.path.join(output_dir, 'field.csv'),
                'method': os.path.join(output_dir, 'method.csv'),
                'variable': os.path.join(output_dir, 'variable.csv'),
            }
            if not os.path.exists(files['class']):
                print(f"Error: class.csv not found in {output_dir}")
                return None
            return files
        except subprocess.CalledProcessError as e:
            print(f"Error executing CK (useJars={use_jars}): {e}")
            print(f"Stderr (tail): {e.stderr[-2000:]}")
            return None
        except subprocess.TimeoutExpired:
            print("[CK] Timeout ao processar. Pulando...")
            return None

    # Tenta padrão (useJars=true) e fallback (false)
    files = _call(True)
    if files is None:
        print("[CK] Tentando fallback com useJars=false ...")
        files = _call(False)
        if files is None:
            return None
    return files


def aggregate_metrics_by_repo(df_class, repo_name):
    """
    Agrega CBO, DIT e LCOM por repositório (estatísticas descritivas).
    """
    metrics = ['cbo', 'dit', 'lcom']
    available_metrics = [metric for metric in metrics if metric in df_class.columns]
    if not available_metrics:
        print(f"[!] No metrics found for {repo_name}")
        return None

    repo_stats = {'repo': repo_name, 'total_classes': len(df_class)}
    for metric in available_metrics:
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
            for stat in ['mean', 'median', 'std', 'min', 'max', 'q1', 'q3']:
                repo_stats[f'{metric}_{stat}'] = None
    return repo_stats


def load_and_print_class_metrics(class_csv_path):
    """
    Lê class.csv e imprime amostra de CBO/DIT/LCOM.
    """
    print("\n[+] Reading CLASS metrics (CBO, DIT, LCOM) ...")
    df_class = pd.read_csv(class_csv_path)
    class_columns = [
        'file', 'class', 'type',
        'cbo',  # Coupling Between Objects
        'dit',  # Depth of Inheritance Tree
        'lcom', # Lack of Cohesion of Methods
    ]
    available_class_cols = [col for col in class_columns if col in df_class.columns]
    print(f"Available metrics: {available_class_cols}")
    print(df_class[available_class_cols].head())


def process_multiple_repos(repo_list_csv, ck_jar_path, output_csv="all_class_metrics.csv"):
    """
    Processa múltiplos repositórios e extrai CBO/DIT/LCOM a nível de classe.
    Tratamento de erros/fallback do CK.
    """
    df_all = []
    repos = pd.read_csv(repo_list_csv)
    for i, row in repos.iterrows():
        repo_url = row["url"]
        print(f"\n=== [{i+1}/{len(repos)}] Processing {repo_url} ===")
        try:
            repo_path = clone_repo(repo_url)  # agora git clone
            csv_paths = run_ck(ck_jar_path, repo_path)
            if csv_paths is None:
                print(f"[!] CK Tool failed for {row['owner']}/{row['name']}")
                continue

            # Load class metrics e filtra colunas
            df_class = pd.read_csv(csv_paths["class"])
            required_columns = ['file', 'class', 'type', 'cbo', 'dit', 'lcom']
            available_columns = [col for col in required_columns if col in df_class.columns]
            df_filtered = df_class[available_columns].copy()
            df_filtered["repo"] = f"{row['owner']}/{row['name']}"
            df_all.append(df_filtered)
            print(f"[+] Extracted {len(df_filtered)} classes with CBO, DIT and LCOM metrics")
        except Exception as e:
            print(f"[!] Failed on {repo_url}: {e}")
            continue
        finally:
            # limpeza do clone
            try:
                if 'repo_path' in locals() and repo_path and os.path.exists(repo_path):
                    _safe_rmtree(repo_path)
            except Exception:
                pass

    if df_all:
        df_final = pd.concat(df_all, ignore_index=True)
        df_final.to_csv(output_csv, index=False)
        print(f"\n[✓] File saved in {output_csv} with {len(df_final)} lines containing CBO, DIT and LCOM metrics.")
    else:
        print("[!] No data was processed successfully.")


def process_multiple_repos_aggregated(repo_list_csv, ck_jar_path, output_csv="aggregated_repo_metrics.csv"):
    """
    Processa múltiplos repositórios e agrega CBO/DIT/LCOM por repo.
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
            if csv_paths is None:
                print(f"[!] CK Tool failed for {repo_name}")
                continue

            if not os.path.exists(csv_paths["class"]):
                print(f"[!] class.csv not found for {repo_name}")
                continue

            df_class = pd.read_csv(csv_paths["class"])
            print(f"[+] Loaded {len(df_class)} classes from {repo_name}")

            if len(df_class) == 0:
                print(f"[!] No Java classes found in {repo_name}")
                continue

            repo_stats = aggregate_metrics_by_repo(df_class, repo_name)
            if repo_stats:
                repo_aggregated_data.append(repo_stats)
                print(f"[+] Aggregated metrics for {repo_name}: {repo_stats['total_classes']} classes")

            if len(repo_aggregated_data) % 10 == 0:
                df_temp = pd.DataFrame(repo_aggregated_data)
                df_temp.to_csv(f"temp_{output_csv}", index=False)
                print(f"[📁] Temporary backup saved with {len(repo_aggregated_data)} repositories")

        except Exception as e:
            print(f"[!] Failed on {repo_url}: {e}")
        finally:
            # cleanup
            try:
                if 'repo_path' in locals() and repo_path and os.path.exists(repo_path):
                    _safe_rmtree(repo_path)
                if 'csv_paths' in locals() and csv_paths:
                    out_dir = os.path.dirname(csv_paths["class"])
                    if os.path.exists(out_dir):
                        _safe_rmtree(out_dir)
            except Exception:
                pass

    if repo_aggregated_data:
        df_aggregated = pd.DataFrame(repo_aggregated_data)
        df_aggregated.to_csv(output_csv, index=False)
        print(f"\n[✓] Aggregated metrics saved in {output_csv} with {len(df_aggregated)} repositories.")

        print(f"\n[📊] Preview of aggregated metrics:")
        display_cols = ['repo', 'total_classes']
        for metric in ['cbo', 'dit', 'lcom']:
            if f'{metric}_mean' in df_aggregated.columns:
                display_cols.append(f'{metric}_mean')
        print(df_aggregated[display_cols].head())

        temp_file = f"temp_{output_csv}"
        if os.path.exists(temp_file):
            os.remove(temp_file)
    else:
        print("[!] No aggregated data was generated.")


def main():
    print("== CK Metrics Extractor - CBO, DIT and LCOM Metrics ==")
    # Opções do menu
    print("\n1. Process multiple repositories - CLASS-level metrics")
    print("2. Process multiple repositories - AGGREGATED metrics by repository")
    print("3. Process a single repository")
    choice = input("Choose an option (1, 2 or 3): ").strip()

    ck_jar_path = os.path.join("ck", "target", "ck-0.7.1-SNAPSHOT-jar-with-dependencies.jar")
    if not os.path.exists(ck_jar_path):
        alt = "ck-0.7.1-SNAPSHOT-jar-with-dependencies.jar"
        if os.path.exists(alt):
            ck_jar_path = alt
        else:
            print(f"Error: {ck_jar_path} not found.")
            print("Place the CK JAR in ck/target/ or in the project root.")
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
        # Process a single repository
        repo_url = input("Enter the GitHub repository URL: ").strip()
        repo_path = clone_repo(repo_url)
        csv_paths = run_ck(ck_jar_path, repo_path)
        if csv_paths is None:
            print("[!] CK failed for single repository.")
            sys.exit(1)
        load_and_print_class_metrics(csv_paths['class'])
        # limpeza
        try:
            if os.path.exists(repo_path):
                _safe_rmtree(repo_path)
            out_dir = os.path.dirname(csv_paths["class"])
            if os.path.exists(out_dir):
                _safe_rmtree(out_dir)
        except Exception:
            pass
    else:
        print("Invalid option.")
        sys.exit(1)


if __name__ == "__main__":
    main()


