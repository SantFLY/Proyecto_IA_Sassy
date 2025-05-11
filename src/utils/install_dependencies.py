import subprocess
import sys
import os
import time

def run_command(command, retries=3, delay=2):
    """Ejecuta un comando con reintentos y delay entre intentos."""
    for attempt in range(retries):
        print(f"\nIntento {attempt + 1} de {retries}")
        print(f"Ejecutando: {command}")
        
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True,
                check=False
            )
            
            if result.returncode == 0:
                print(f"✅ Éxito: {result.stdout}")
                return True
            else:
                print(f"❌ Error: {result.stderr}")
                if attempt < retries - 1:
                    print(f"Esperando {delay} segundos antes de reintentar...")
                    time.sleep(delay)
                continue
                
        except Exception as e:
            print(f"❌ Error inesperado: {str(e)}")
            if attempt < retries - 1:
                print(f"Esperando {delay} segundos antes de reintentar...")
                time.sleep(delay)
            continue
    
    return False

def install_dependencies():
    print("\n=== INSTALANDO DEPENDENCIAS ===\n")
    
    # 1. Instalar dependencias base (las más estables)
    print("\n1. Instalando dependencias base...")
    base_deps = [
        "numpy>=1.21.0",
        "python-dotenv==1.0.0",
        "requests>=2.31.0",
        "psutil==5.9.8",
        "python-dateutil==2.8.2",
        "tqdm>=4.65.0",
        "colorama>=0.4.6",
        "rich>=13.0.0"
    ]
    
    for dep in base_deps:
        if not run_command(f"pip install {dep}"):
            print(f"⚠️ Error instalando {dep}")
            return False

    # 2. Instalar dependencias de GUI (separadas por compatibilidad)
    print("\n2. Instalando dependencias de GUI...")
    gui_deps = [
        "PyQt5==5.15.9",
        "PySide6>=6.8.0",
        "PyOpenGL==3.1.7"
    ]
    
    for dep in gui_deps:
        if not run_command(f"pip install {dep}"):
            print(f"⚠️ Error instalando {dep}")
            return False

    # 3. Instalar PyTorch y dependencias relacionadas
    print("\n3. Instalando PyTorch y dependencias...")
    torch_deps = [
        "--find-links https://download.pytorch.org/whl/torch_stable.html torch>=2.0.0",
        "--find-links https://download.pytorch.org/whl/torch_stable.html torchvision>=0.15.0"
    ]
    
    for dep in torch_deps:
        if not run_command(f"pip install {dep}"):
            print(f"⚠️ Error instalando {dep}")
            return False

    # 4. Instalar dependencias de procesamiento de datos
    print("\n4. Instalando dependencias de procesamiento de datos...")
    data_deps = [
        "pandas>=1.3.0",
        "scipy>=1.7.0",
        "scikit-learn>=0.24.0"
    ]
    
    for dep in data_deps:
        if not run_command(f"pip install {dep}"):
            print(f"⚠️ Error instalando {dep}")
            return False

    # 5. Instalar dependencias de NLP (una por una para mejor control)
    print("\n5. Instalando dependencias de NLP...")
    nlp_deps = [
        "nltk>=3.8.1",
        "transformers>=4.30.0",
        "--find-links https://github.com/kdexd/scipy-wheels/releases/download/v0.1.0/ sentencepiece",
        "sentence-transformers==2.2.2"
    ]
    
    for dep in nlp_deps:
        if not run_command(f"pip install {dep}"):
            print(f"⚠️ Error instalando {dep}")
            return False

    # 6. Instalar dependencias de seguridad
    print("\n6. Instalando dependencias de seguridad...")
    security_deps = [
        "yara-python>=4.3.0",
        "python-magic-bin>=0.4.14" if sys.platform == "win32" else "python-magic>=0.4.27",
        "pefile>=2023.2.7",
        "pywin32>=306" if sys.platform == "win32" else "",
        "geoip2>=4.7.0"
    ]
    
    for dep in security_deps:
        if dep and not run_command(f"pip install {dep}"):
            print(f"⚠️ Error instalando {dep}")
            return False

    # 7. Instalar dependencias de desarrollo
    print("\n7. Instalando dependencias de desarrollo...")
    dev_deps = [
        "pytest>=7.0.0",
        "pytest-cov>=4.1.0",
        "black>=23.0.0",
        "isort>=5.12.0",
        "flake8>=6.0.0"
    ]
    
    for dep in dev_deps:
        if not run_command(f"pip install {dep}"):
            print(f"⚠️ Error instalando {dep}")
            return False

    print("\n✅ ¡Todas las dependencias se han instalado correctamente!")
    return True

if __name__ == "__main__":
    print("=== INICIANDO INSTALACIÓN DE DEPENDENCIAS ===\n")
    print(f"Python version: {sys.version}")
    print(f"Sistema operativo: {sys.platform}")
    print(f"Directorio actual: {os.getcwd()}\n")
    
    if install_dependencies():
        print("\n✅ Instalación completada con éxito.")
    else:
        print("\n❌ Hubo errores durante la instalación.")
        print("Por favor, revisa los mensajes de error arriba.")
        sys.exit(1) 