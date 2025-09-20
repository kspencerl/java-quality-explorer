import os
import shutil
import subprocess
import sys
import pandas as pd
from git import Repo

def clone_repo(repo_url, dest_dir='repo'):
    """
    Baixa e descompacta o repositório GitHub informado como ZIP para um diretório local.
    Se o diretório já existir, ele será removido antes de baixar novamente.
    """
    import requests
    import zipfile
    from io import BytesIO

    if os.path.exists(dest_dir):
        shutil.rmtree(dest_dir)

    print(f"[+] Preparando download do ZIP de {repo_url} ...")
    # Extrai owner e repo do URL
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

    print(f"[+] Baixando ZIP: {zip_url}")
    response = requests.get(zip_url)
    if response.status_code != 200:
        print(f"Erro ao baixar ZIP: {zip_url}")
        sys.exit(1)

    with zipfile.ZipFile(BytesIO(response.content)) as zip_ref:
        zip_ref.extractall(dest_dir)

    extracted_dir = os.path.join(dest_dir, f"{repo_name}-{default_branch}")
    if not os.path.exists(extracted_dir):
        print(f"Erro: diretório extraído não encontrado: {extracted_dir}")
        sys.exit(1)
    return extracted_dir

def run_ck(jar_path, repo_dir, output_dir=None):
    """
    Executa o CK Tool e retorna os caminhos para os arquivos .csv gerados.
    """
    # Cria um diretório único para cada repositório se não especificado
    if output_dir is None:
        import time
        timestamp = int(time.time())
        output_dir = f'ck_output_{timestamp}'
    
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)

    print(f"[+] Executando CK Tool nas fontes em {repo_dir} ...")
    print(f"[+] Salvando resultados em {output_dir} ...")
    
    cmd = [
        'java', '-jar', jar_path,
        repo_dir,
        'true',      # usar JARs
        '0',         # max files per partition = automático
        'false',     # NÃO extrair métricas de variáveis e campos (só classes)
        output_dir + os.sep
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar o CK: {e}")
        print(f"Stderr: {e.stderr}")
        return None

    # Caminhos para os arquivos gerados
    files = {
        'class': os.path.join(output_dir, 'class.csv'),
        'field': os.path.join(output_dir, 'field.csv'),
        'method': os.path.join(output_dir, 'method.csv'),
        'variable': os.path.join(output_dir, 'variable.csv'),
    }

    # Confirma se class.csv existe
    if not os.path.exists(files['class']):
        print(f"Erro: class.csv não encontrado em {output_dir}")
        return None

    return files

def aggregate_metrics_by_repo(df_class, repo_name):
    """
    Agrega métricas CBO, DIT e LCOM por repositório.
    Calcula estatísticas descritivas para cada métrica.
    """
    metrics = ['cbo', 'dit', 'lcom']
    available_metrics = [metric for metric in metrics if metric in df_class.columns]
    
    if not available_metrics:
        print(f"[!] Nenhuma métrica encontrada para {repo_name}")
        return None
    
    # Calcula estatísticas para cada métrica
    repo_stats = {'repo': repo_name, 'total_classes': len(df_class)}
    
    for metric in available_metrics:
        # Remove valores NaN/nulos para cálculos
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
            # Valores padrão se não há dados válidos
            for stat in ['mean', 'median', 'std', 'min', 'max', 'q1', 'q3']:
                repo_stats[f'{metric}_{stat}'] = None
    
    return repo_stats


def load_and_print_class_metrics(class_csv_path):
    """
    Carrega métricas por classe do CSV, seleciona apenas CBO, DIT e LCOM e imprime as primeiras linhas.
    """
    print("\n[+] Lendo métricas por CLASSE (CBO, DIT, LCOM) ...")
    df_class = pd.read_csv(class_csv_path)

    # Colunas necessárias: identificação + métricas CBO, DIT e LCOM
    class_columns = [
        'file', 'class', 'type',
        'cbo',   # Coupling Between Objects
        'dit',   # Depth of Inheritance Tree
        'lcom',  # Lack of Cohesion of Methods
    ]

    available_class_cols = [col for col in class_columns if col in df_class.columns]
    print(f"Métricas disponíveis: {available_class_cols}")
    print(df_class[available_class_cols].head())  # Exibe as 5 primeiras linhas


def process_multiple_repos(repo_list_csv, ck_jar_path, output_csv="all_class_metrics.csv"):
    """
    Processa múltiplos repositórios e extrai apenas as métricas CBO, DIT e LCOM.
    Salva o resultado em um único CSV consolidado.
    """
    df_all = []

    repos = pd.read_csv(repo_list_csv)
    for i, row in repos.iterrows():
        repo_url = row["url"]
        print(f"\n=== [{i+1}/{len(repos)}] Processando {repo_url} ===")
        try:
            repo_path = clone_repo(repo_url)
            csv_paths = run_ck(ck_jar_path, repo_path)

            # Carrega métricas de classe e filtra apenas as colunas necessárias
            df_class = pd.read_csv(csv_paths["class"])
            
            # Seleciona apenas as colunas de identificação e as métricas CBO, DIT e LCOM
            required_columns = ['file', 'class', 'type', 'cbo', 'dit', 'lcom']
            available_columns = [col for col in required_columns if col in df_class.columns]
            
            df_filtered = df_class[available_columns].copy()
            df_filtered["repo"] = f"{row['owner']}/{row['name']}"
            df_all.append(df_filtered)
            
            print(f"[+] Extraídas {len(df_filtered)} classes com métricas CBO, DIT e LCOM")
            
        except Exception as e:
            print(f"[!] Falha em {repo_url}: {e}")
            continue

    # Consolida tudo
    if df_all:
        df_final = pd.concat(df_all, ignore_index=True)
        df_final.to_csv(output_csv, index=False)
        print(f"\n[✓] Arquivo salvo em {output_csv} com {len(df_final)} linhas contendo métricas CBO, DIT e LCOM.")
    else:
        print("[!] Nenhum dado foi processado com sucesso.")


def process_multiple_repos_aggregated(repo_list_csv, ck_jar_path, output_csv="aggregated_repo_metrics.csv"):
    """
    Processa múltiplos repositórios e agrega as métricas CBO, DIT e LCOM por repositório.
    Salva estatísticas agregadas (média, mediana, etc.) em um CSV consolidado.
    """
    repo_aggregated_data = []

    repos = pd.read_csv(repo_list_csv)
    for i, row in repos.iterrows():
        repo_url = row["url"]
        repo_name = f"{row['owner']}/{row['name']}"
        print(f"\n=== [{i+1}/{len(repos)}] Processando {repo_url} ===")
        
        try:
            repo_path = clone_repo(repo_url)
            csv_paths = run_ck(ck_jar_path, repo_path)
            
            # Verifica se o CK foi executado com sucesso
            if csv_paths is None:
                print(f"[!] CK Tool falhou para {repo_name}")
                continue
                
            # Verifica se o arquivo class.csv existe e tem conteúdo
            if not os.path.exists(csv_paths["class"]):
                print(f"[!] class.csv não encontrado para {repo_name}")
                continue

            # Carrega métricas de classe
            df_class = pd.read_csv(csv_paths["class"])
            print(f"[+] Carregadas {len(df_class)} classes de {repo_name}")
            
            # Se não há classes Java, pula o repositório
            if len(df_class) == 0:
                print(f"[!] Nenhuma classe Java encontrada em {repo_name}")
                continue
            
            # Agrega métricas por repositório
            repo_stats = aggregate_metrics_by_repo(df_class, repo_name)
            
            if repo_stats:
                repo_aggregated_data.append(repo_stats)
                print(f"[+] Métricas agregadas para {repo_name}: {repo_stats['total_classes']} classes")
                
                # Salva dados progressivamente para evitar perda em caso de interrupção
                if len(repo_aggregated_data) % 10 == 0:  # A cada 10 repositórios
                    df_temp = pd.DataFrame(repo_aggregated_data)
                    df_temp.to_csv(f"temp_{output_csv}", index=False)
                    print(f"[📁] Backup temporário salvo com {len(repo_aggregated_data)} repositórios")
            
        except Exception as e:
            print(f"[!] Falha em {repo_url}: {e}")
            continue
        
        # Cleanup: remove diretórios temporários
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
            pass  # Ignora erros de cleanup

    # Salva dados agregados finais
    if repo_aggregated_data:
        df_aggregated = pd.DataFrame(repo_aggregated_data)
        df_aggregated.to_csv(output_csv, index=False)
        print(f"\n[✓] Métricas agregadas salvas em {output_csv} com {len(df_aggregated)} repositórios.")
        
        # Mostra preview das estatísticas
        print(f"\n[📊] Preview das métricas agregadas:")
        display_cols = ['repo', 'total_classes']
        for metric in ['cbo', 'dit', 'lcom']:
            if f'{metric}_mean' in df_aggregated.columns:
                display_cols.append(f'{metric}_mean')
        print(df_aggregated[display_cols].head())
        
        # Remove arquivo temporário se existe
        temp_file = f"temp_{output_csv}"
        if os.path.exists(temp_file):
            os.remove(temp_file)
        
    else:
        print("[!] Nenhum dado agregado foi gerado.")


def main():
    print("== CK Metrics Extractor - Métricas CBO, DIT e LCOM ==")
    
    # Opções de processamento
    print("\n1. Processar múltiplos repositórios - métricas por CLASSE")
    print("2. Processar múltiplos repositórios - métricas AGREGADAS por repositório")
    print("3. Processar um único repositório")
    choice = input("Escolha uma opção (1, 2 ou 3): ").strip()
    
    ck_jar_path = os.path.join("ck", "target", "ck-0.7.1-SNAPSHOT-jar-with-dependencies.jar")
    
    if not os.path.exists(ck_jar_path):
        print(f"Erro: {ck_jar_path} não encontrado.")
        print("Execute os comandos no README para baixar e compilar o CK Tool.")
        sys.exit(1)
    
    if choice in ["1", "2"]:
        # Processar múltiplos repositórios
        csv_file = input("Informe o caminho para o CSV com os repositórios (ex: repositories.csv): ").strip()
        if not os.path.exists(csv_file):
            print(f"Erro: arquivo {csv_file} não encontrado.")
            sys.exit(1)
        
        if choice == "1":
            # Métricas por classe
            output_file = input("Nome do arquivo de saída (padrão: all_class_metrics.csv): ").strip()
            if not output_file:
                output_file = "all_class_metrics.csv"
            
            print(f"\n[+] Processando repositórios (métricas por classe) do arquivo {csv_file}...")
            process_multiple_repos(csv_file, ck_jar_path, output_file)
            
        elif choice == "2":
            # Métricas agregadas por repositório
            output_file = input("Nome do arquivo de saída (padrão: aggregated_repo_metrics.csv): ").strip()
            if not output_file:
                output_file = "aggregated_repo_metrics.csv"
            
            print(f"\n[+] Processando repositórios (métricas agregadas) do arquivo {csv_file}...")
            process_multiple_repos_aggregated(csv_file, ck_jar_path, output_file)
        
    elif choice == "3":
        # Processar um único repositório (modo original simplificado)
        repo_url = input("Informe a URL do repositório GitHub: ").strip()
        
        # Clona o repositório e executa o CK
        repo_path = clone_repo(repo_url)
        csv_paths = run_ck(ck_jar_path, repo_path)
        
        # Processa apenas métricas de classe com CBO, DIT e LCOM
        load_and_print_class_metrics(csv_paths['class'])
        
    else:
        print("Opção inválida.")
        sys.exit(1)

if __name__ == "__main__":
    main()

# Baixe o CK Tool e monte o JAR file (ck/target/ck-0.7.1-SNAPSHOT-jar-with-dependencies.jar):
# git clone https://github.com/mauricioaniche/ck.git
# cd ck
# mvn clean package
# Documentação: https://github.com/mauricioaniche/ck

# Instale as dependências necessárias deste projeto:
# pip install gitpython pandas requests

# Execute o script:
# python ck_metrics_extractor.py

# Repositórios de exemplo:
# - Único: https://github.com/spring-projects/spring-petclinic
# - Múltiplos: use repositories.csv com colunas: url, owner, name

# Opções de saída:
# 1. Métricas por CLASSE: CSV com uma linha por classe (all_class_metrics.csv)
# 2. Métricas AGREGADAS: CSV com uma linha por repositório com estatísticas (aggregated_repo_metrics.csv)
#    - Inclui: média, mediana, desvio padrão, min, max, quartis para cada métrica

# Métricas extraídas (apenas):
# - CBO: Coupling Between Objects (Acoplamento entre Objetos)
# - DIT: Depth of Inheritance Tree (Profundidade da Árvore de Herança)
# - LCOM: Lack of Cohesion of Methods (Falta de Coesão dos Métodos)