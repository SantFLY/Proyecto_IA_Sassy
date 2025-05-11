# 🤖 Sassy - Asistente Virtual Inteligente

<div align="center">
  <img src="src/gui/resources/bombilla.png" alt="Sassy Logo" width="200"/>
  
  [![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
  [![PyQt5](https://img.shields.io/badge/PyQt5-5.15%2B-green)](https://www.riverbankcomputing.com/software/pyqt/)
  [![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
  [![Status](https://img.shields.io/badge/Status-Active-success)](https://github.com/yourusername/sassy)
</div>

## 📋 Índice
- [Descripción](#-descripción)
- [Características](#-características)
- [Requisitos](#-requisitos)
- [Instalación](#-instalación)
- [Uso](#-uso)
- [Arquitectura](#-arquitectura)
- [Módulos Principales](#-módulos-principales)
- [Contribución](#-contribución)
- [Licencia](#-licencia)
- [Contacto](#-contacto)

## 🌟 Descripción

Sassy es un asistente virtual inteligente de última generación que combina una interfaz gráfica moderna con capacidades avanzadas de procesamiento de lenguaje natural y aprendizaje automático. Diseñado para ofrecer una experiencia de usuario fluida y profesional, Sassy integra múltiples sistemas backend en una arquitectura modular y escalable.

## ✨ Características

### 🎨 Interfaz Gráfica
- Diseño moderno y adaptable con PyQt5
- Tema claro/oscuro personalizable
- Animaciones fluidas y feedback visual avanzado
- Sistema de notificaciones tipo toast
- Paneles modulares y redimensionables

### 🧠 Capacidades Inteligentes
- Procesamiento de lenguaje natural avanzado
- Sistema de memoria contextual
- Gestión emocional adaptativa
- Aprendizaje continuo
- Proactividad inteligente

### 🛡️ Seguridad
- Sistema antivirus integrado
- Firewall personalizado
- Monitoreo de seguridad en tiempo real
- Logs detallados de actividad

### 📊 Monitoreo y Control
- Panel de estado en tiempo real
- Sistema de logs avanzado
- Control manual de funciones
- Configuración personalizable

## 📋 Requisitos

### Sistema Operativo
- Windows 10/11
- Linux (Ubuntu 20.04+)
- macOS 10.15+

### Dependencias
```bash
Python >= 3.8
PyQt5 >= 5.15
numpy >= 1.19
pandas >= 1.3
scikit-learn >= 0.24
```

## 💻 Instalación

1. Clonar el repositorio:
```bash
git clone https://github.com/SantFLY/sassy.git
cd sassy
```

2. Crear y activar entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Configurar variables de entorno:
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

## 🚀 Uso

### Iniciar Sassy
```bash
python src/main.py
```

### Comandos Principales
- `Ctrl + Space`: Activar/desactivar asistente
- `Ctrl + M`: Abrir menú principal
- `Ctrl + L`: Ver logs
- `Ctrl + S`: Configuración

## 🏗️ Arquitectura

### Estructura del Proyecto
```
sassy/
├── src/
│   ├── core/           # Núcleo del asistente
│   ├── gui/            # Componentes de interfaz
│   ├── adapters/       # Adaptadores de sistemas
│   ├── systems/        # Sistemas backend
│   └── utils/          # Utilidades
├── tests/              # Pruebas unitarias
├── docs/               # Documentación
└── assets/            # Recursos
```

### Componentes Principales
- **Core**: Motor principal del asistente
- **GUI**: Interfaz gráfica modular
- **Adapters**: Conexión entre sistemas
- **Systems**: Funcionalidades backend
- **Utils**: Herramientas auxiliares

## 📦 Módulos Principales

### Core
- Gestión de comandos
- Procesamiento de lenguaje
- Sistema de memoria
- Gestión emocional

### GUI
- Ventana principal
- Paneles modulares
- Sistema de notificaciones
- Temas y estilos

### Sistemas
- Antivirus
- Firewall
- Proactividad
- Aprendizaje
- Logs

## 🤝 Contribución

1. Fork el proyecto
2. Crear rama feature (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## 📞 Contacto

Santiago Polanco - [@SantFLY](https://github.com/SantFLY)

Discord: SantFLY Server EL OLIMPO

---

<div align="center">
  <sub>Built with ❤️ by Santiago Polanco</sub>
</div> 