#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
analizar_proyecto.py — Análisis estático de proyecto Python
===========================================================
Script monolítico que, al ejecutarse, recorre todos los archivos .py
ubicados en su mismo directorio y subdirectorios, y genera un informe
detallado en un archivo .txt con la estructura modular del proyecto y
los elementos relevantes de cada archivo.

El informe está diseñado para ser entregado a un agente de código que,
sin necesidad de leer los archivos fuente completos, pueda comprender
el funcionamiento general del proyecto, sus módulos, clases, funciones,
dependencias e interrelaciones.

Uso:
    python analizar_proyecto.py

Salida:
    INFORME_PROYECTO.txt  (en el mismo directorio del script)
"""

import ast
import os
import sys
import textwrap
from collections import defaultdict
from datetime import datetime
from pathlib import Path

# ─────────────────────────────────────────────────────────────
# CONFIGURACIÓN
# ─────────────────────────────────────────────────────────────
NOMBRE_INFORME = "INFORME_PROYECTO.txt"
SELF_NAME = os.path.basename(__file__)
# Directorios a ignorar
DIRS_IGNORADOS = {
    "__pycache__", ".git", ".venv", "venv", "env", ".env",
    "node_modules", ".tox", ".mypy_cache", ".pytest_cache",
    "dist", "build", "egg-info",
}
MAX_LINEAS_DOCSTRING = 15  # Límite de líneas de docstring a incluir


# ─────────────────────────────────────────────────────────────
# UTILIDADES
# ─────────────────────────────────────────────────────────────

def contar_lineas(ruta: str) -> int:
    """Cuenta líneas totales de un archivo."""
    try:
        with open(ruta, encoding="utf-8", errors="replace") as f:
            return sum(1 for _ in f)
    except OSError:
        return 0


def leer_fuente(ruta: str) -> str:
    """Lee el contenido fuente de un archivo .py."""
    with open(ruta, encoding="utf-8", errors="replace") as f:
        return f.read()


def truncar_docstring(doc: str | None) -> str:
    """Devuelve el docstring truncado si es muy largo."""
    if not doc:
        return ""
    lineas = doc.strip().splitlines()
    if len(lineas) > MAX_LINEAS_DOCSTRING:
        lineas = lineas[:MAX_LINEAS_DOCSTRING] + ["  ... (truncado)"]
    return "\n".join(lineas)


def obtener_nombre_decoradores(nodo: ast.AST) -> list[str]:
    """Extrae los nombres legibles de los decoradores de un nodo."""
    decoradores = []
    for dec in getattr(nodo, "decorator_list", []):
        if isinstance(dec, ast.Name):
            decoradores.append(f"@{dec.id}")
        elif isinstance(dec, ast.Attribute):
            decoradores.append(f"@{ast.dump(dec)}"[:60])
        elif isinstance(dec, ast.Call):
            func = dec.func
            if isinstance(func, ast.Name):
                decoradores.append(f"@{func.id}(...)")
            elif isinstance(func, ast.Attribute):
                decoradores.append(f"@{ast.unparse(func)}(...)")
            else:
                decoradores.append(f"@{ast.unparse(dec)}"[:60])
        else:
            decoradores.append(f"@{ast.unparse(dec)}"[:60])
    return decoradores


def obtener_firma_funcion(nodo: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    """Genera la firma legible de una función/método."""
    args = nodo.args
    partes = []

    # Argumentos posicionales
    total_args = len(args.args)
    total_defaults = len(args.defaults)
    offset = total_args - total_defaults

    for i, arg in enumerate(args.args):
        nombre = arg.arg
        tipo = ""
        if arg.annotation:
            try:
                tipo = f": {ast.unparse(arg.annotation)}"
            except Exception:
                tipo = ""
        default_idx = i - offset
        if default_idx >= 0 and default_idx < len(args.defaults):
            try:
                val = ast.unparse(args.defaults[default_idx])
            except Exception:
                val = "..."
            partes.append(f"{nombre}{tipo}={val}")
        else:
            partes.append(f"{nombre}{tipo}")

    # *args
    if args.vararg:
        partes.append(f"*{args.vararg.arg}")
    # keyword-only
    for i, arg in enumerate(args.kwonlyargs):
        nombre = arg.arg
        if i < len(args.kw_defaults) and args.kw_defaults[i] is not None:
            try:
                val = ast.unparse(args.kw_defaults[i])
            except Exception:
                val = "..."
            partes.append(f"{nombre}={val}")
        else:
            partes.append(nombre)
    # **kwargs
    if args.kwarg:
        partes.append(f"**{args.kwarg.arg}")

    retorno = ""
    if nodo.returns:
        try:
            retorno = f" -> {ast.unparse(nodo.returns)}"
        except Exception:
            retorno = ""

    prefix = "async def" if isinstance(nodo, ast.AsyncFunctionDef) else "def"
    return f"{prefix} {nodo.name}({', '.join(partes)}){retorno}"


def es_constante(nombre: str) -> bool:
    """Heurística: un nombre en MAYÚSCULAS_CON_GUIONES es constante."""
    return nombre.isupper() and not nombre.startswith("_")


# ─────────────────────────────────────────────────────────────
# ANÁLISIS AST DE UN ARCHIVO
# ─────────────────────────────────────────────────────────────

class InfoArchivo:
    """Contiene toda la información extraída de un archivo .py."""

    def __init__(self, ruta_absoluta: str, ruta_relativa: str):
        self.ruta_absoluta = ruta_absoluta
        self.ruta_relativa = ruta_relativa
        self.lineas_totales = 0
        self.docstring_modulo = ""
        self.imports: list[str] = []
        self.imports_from: list[str] = []
        self.constantes: list[str] = []  # "NOMBRE = valor"
        self.variables_globales: list[str] = []
        self.funciones: list[dict] = []
        self.clases: list[dict] = []
        self.error_parseo: str | None = None

    def analizar(self) -> None:
        """Realiza el análisis AST completo del archivo."""
        self.lineas_totales = contar_lineas(self.ruta_absoluta)
        try:
            fuente = leer_fuente(self.ruta_absoluta)
        except OSError as e:
            self.error_parseo = f"No se pudo leer: {e}"
            return

        try:
            arbol = ast.parse(fuente, filename=self.ruta_relativa)
        except SyntaxError as e:
            self.error_parseo = f"Error de sintaxis: {e}"
            return

        # Docstring del módulo
        self.docstring_modulo = truncar_docstring(ast.get_docstring(arbol))

        # Recorrer nodos de primer nivel
        for nodo in ast.iter_child_nodes(arbol):
            if isinstance(nodo, ast.Import):
                for alias in nodo.names:
                    self.imports.append(alias.name)
            elif isinstance(nodo, ast.ImportFrom):
                modulo = nodo.module or ""
                nombres = ", ".join(a.name for a in nodo.names)
                self.imports_from.append(f"from {modulo} import {nombres}")
            elif isinstance(nodo, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self._extraer_funcion(nodo)
            elif isinstance(nodo, ast.ClassDef):
                self._extraer_clase(nodo)
            elif isinstance(nodo, ast.Assign):
                self._extraer_asignacion(nodo)
            elif isinstance(nodo, ast.AnnAssign):
                self._extraer_anotacion_global(nodo)

    def _extraer_funcion(self, nodo: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        firma = obtener_firma_funcion(nodo)
        decoradores = obtener_nombre_decoradores(nodo)
        doc = truncar_docstring(ast.get_docstring(nodo))
        self.funciones.append({
            "firma": firma,
            "decoradores": decoradores,
            "docstring": doc,
            "linea": nodo.lineno,
        })

    def _extraer_clase(self, nodo: ast.ClassDef) -> None:
        bases = []
        for base in nodo.bases:
            try:
                bases.append(ast.unparse(base))
            except Exception:
                bases.append("?")
        decoradores_cls = obtener_nombre_decoradores(nodo)
        doc_cls = truncar_docstring(ast.get_docstring(nodo))

        metodos = []
        atributos_init: list[str] = []
        atributos_clase: list[str] = []

        for sub in ast.iter_child_nodes(nodo):
            if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef)):
                firma = obtener_firma_funcion(sub)
                decs = obtener_nombre_decoradores(sub)
                doc_m = truncar_docstring(ast.get_docstring(sub))
                metodos.append({
                    "firma": firma,
                    "decoradores": decs,
                    "docstring": doc_m,
                    "linea": sub.lineno,
                })
                # Extraer atributos self.xxx del __init__
                if sub.name == "__init__":
                    for stmt in ast.walk(sub):
                        if isinstance(stmt, ast.Assign):
                            for target in stmt.targets:
                                if (isinstance(target, ast.Attribute)
                                        and isinstance(target.value, ast.Name)
                                        and target.value.id == "self"):
                                    atributos_init.append(f"self.{target.attr}")
                        elif isinstance(stmt, ast.AnnAssign):
                            target = stmt.target
                            if (isinstance(target, ast.Attribute)
                                    and isinstance(target.value, ast.Name)
                                    and target.value.id == "self"):
                                try:
                                    ann = ast.unparse(stmt.annotation)
                                except Exception:
                                    ann = "?"
                                atributos_init.append(f"self.{target.attr}: {ann}")

            elif isinstance(sub, ast.Assign):
                for target in sub.targets:
                    if isinstance(target, ast.Name):
                        try:
                            val = ast.unparse(sub.value)[:80]
                        except Exception:
                            val = "..."
                        atributos_clase.append(f"{target.id} = {val}")
            elif isinstance(sub, ast.AnnAssign) and isinstance(sub.target, ast.Name):
                try:
                    ann = ast.unparse(sub.annotation)
                except Exception:
                    ann = "?"
                nombre = sub.target.id
                if sub.value:
                    try:
                        val = ast.unparse(sub.value)[:80]
                    except Exception:
                        val = "..."
                    atributos_clase.append(f"{nombre}: {ann} = {val}")
                else:
                    atributos_clase.append(f"{nombre}: {ann}")

        self.clases.append({
            "nombre": nodo.name,
            "bases": bases,
            "decoradores": decoradores_cls,
            "docstring": doc_cls,
            "metodos": metodos,
            "atributos_init": sorted(set(atributos_init)),
            "atributos_clase": atributos_clase,
            "linea": nodo.lineno,
        })

    def _extraer_asignacion(self, nodo: ast.Assign) -> None:
        for target in nodo.targets:
            if isinstance(target, ast.Name):
                nombre = target.id
                try:
                    valor = ast.unparse(nodo.value)[:100]
                except Exception:
                    valor = "..."
                if es_constante(nombre):
                    self.constantes.append(f"{nombre} = {valor}")
                elif not nombre.startswith("_"):
                    self.variables_globales.append(f"{nombre} = {valor}")

    def _extraer_anotacion_global(self, nodo: ast.AnnAssign) -> None:
        if isinstance(nodo.target, ast.Name):
            nombre = nodo.target.id
            try:
                ann = ast.unparse(nodo.annotation)
            except Exception:
                ann = "?"
            linea = f"{nombre}: {ann}"
            if nodo.value:
                try:
                    linea += f" = {ast.unparse(nodo.value)[:80]}"
                except Exception:
                    pass
            if es_constante(nombre):
                self.constantes.append(linea)
            elif not nombre.startswith("_"):
                self.variables_globales.append(linea)


# ─────────────────────────────────────────────────────────────
# DESCUBRIMIENTO DE ARCHIVOS
# ─────────────────────────────────────────────────────────────

def descubrir_archivos_py(raiz: str) -> list[str]:
    """Descubre todos los archivos .py bajo *raiz*, ignorando dirs configurados."""
    archivos = []
    for dirpath, dirnames, filenames in os.walk(raiz):
        # Podar directorios ignorados
        dirnames[:] = [
            d for d in dirnames
            if d not in DIRS_IGNORADOS and not d.endswith(".egg-info")
        ]
        for fname in sorted(filenames):
            if fname.endswith(".py") and fname != SELF_NAME:
                archivos.append(os.path.join(dirpath, fname))
    return archivos


# ─────────────────────────────────────────────────────────────
# GENERACIÓN DEL ÁRBOL DE DIRECTORIOS
# ─────────────────────────────────────────────────────────────

def generar_arbol(raiz: str, archivos_py: list[str]) -> str:
    """Genera una representación visual de árbol del proyecto."""
    rel_paths = [os.path.relpath(a, raiz) for a in archivos_py]
    # Agrupar por directorio
    dirs: dict[str, list[str]] = defaultdict(list)
    for rp in rel_paths:
        carpeta = os.path.dirname(rp) or "."
        dirs[carpeta].append(os.path.basename(rp))

    lineas = [f"{os.path.basename(raiz)}/"]
    carpetas_ordenadas = sorted(dirs.keys())
    for i, carpeta in enumerate(carpetas_ordenadas):
        es_ultimo_dir = (i == len(carpetas_ordenadas) - 1)
        prefijo_dir = "└── " if es_ultimo_dir else "├── "
        prefijo_hijo = "    " if es_ultimo_dir else "│   "

        if carpeta != ".":
            lineas.append(f"{prefijo_dir}{carpeta}/")
        else:
            prefijo_hijo = ""

        archivos = sorted(dirs[carpeta])
        for j, arch in enumerate(archivos):
            es_ultimo = (j == len(archivos) - 1)
            conector = "└── " if es_ultimo else "├── "
            lineas.append(f"{prefijo_hijo}{conector}{arch}")

    return "\n".join(lineas)


# ─────────────────────────────────────────────────────────────
# ANÁLISIS DE DEPENDENCIAS ENTRE MÓDULOS
# ─────────────────────────────────────────────────────────────

def analizar_dependencias_internas(archivos_info: list[InfoArchivo]) -> dict[str, list[str]]:
    """Determina qué módulos del proyecto importa cada archivo."""
    # Nombres de módulos presentes en el proyecto (sin extensión)
    modulos_proyecto = set()
    for info in archivos_info:
        nombre = Path(info.ruta_relativa).stem
        modulos_proyecto.add(nombre)

    dependencias: dict[str, list[str]] = {}
    for info in archivos_info:
        deps = []
        for imp in info.imports:
            modulo_base = imp.split(".")[0]
            if modulo_base in modulos_proyecto:
                deps.append(imp)
        for imp_from in info.imports_from:
            # "from modulo import ..."
            partes = imp_from.split()
            if len(partes) >= 2:
                modulo_base = partes[1].split(".")[0]
                if modulo_base in modulos_proyecto:
                    deps.append(imp_from)
        if deps:
            dependencias[info.ruta_relativa] = deps

    return dependencias


def analizar_dependencias_externas(archivos_info: list[InfoArchivo]) -> dict[str, int]:
    """Cuenta las dependencias externas (librerías de terceros)."""
    stdlib = {
        "os", "sys", "ast", "re", "json", "csv", "math", "time", "datetime",
        "pathlib", "collections", "functools", "itertools", "operator",
        "typing", "abc", "enum", "dataclasses", "copy", "io", "string",
        "textwrap", "struct", "hashlib", "hmac", "secrets", "base64",
        "sqlite3", "subprocess", "threading", "multiprocessing", "queue",
        "socket", "http", "urllib", "email", "html", "xml", "logging",
        "unittest", "doctest", "argparse", "configparser", "shutil",
        "tempfile", "glob", "fnmatch", "stat", "contextlib", "warnings",
        "traceback", "inspect", "importlib", "pkgutil", "pprint",
        "platform", "signal", "ctypes", "webbrowser", "uuid",
        "concurrent", "asyncio", "ssl", "zipfile", "tarfile", "gzip",
        "pickle", "shelve", "dbm", "winreg", "msvcrt", "winsound",
    }
    modulos_proyecto = set()
    for info in archivos_info:
        modulos_proyecto.add(Path(info.ruta_relativa).stem)

    conteo: dict[str, int] = defaultdict(int)
    for info in archivos_info:
        for imp in info.imports:
            mod = imp.split(".")[0]
            if mod not in stdlib and mod not in modulos_proyecto:
                conteo[mod] += 1
        for imp_from in info.imports_from:
            partes = imp_from.split()
            if len(partes) >= 2:
                mod = partes[1].split(".")[0]
                if mod not in stdlib and mod not in modulos_proyecto:
                    conteo[mod] += 1
    return dict(sorted(conteo.items(), key=lambda x: -x[1]))


# ─────────────────────────────────────────────────────────────
# FORMATEADOR DEL INFORME
# ─────────────────────────────────────────────────────────────

def separador(titulo: str, char: str = "=") -> str:
    ancho = 72
    return f"\n{char * ancho}\n  {titulo}\n{char * ancho}\n"


def formatear_informe(
    raiz: str,
    archivos_info: list[InfoArchivo],
    arbol: str,
    deps_internas: dict[str, list[str]],
    deps_externas: dict[str, int],
) -> str:
    """Genera el texto completo del informe."""
    lineas: list[str] = []

    # ── Encabezado ──
    lineas.append("=" * 72)
    lineas.append("  INFORME DE ANÁLISIS DEL PROYECTO")
    lineas.append("=" * 72)
    lineas.append(f"  Directorio raíz : {raiz}")
    lineas.append(f"  Fecha           : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lineas.append(f"  Archivos .py    : {len(archivos_info)}")
    total_lineas = sum(i.lineas_totales for i in archivos_info)
    lineas.append(f"  Líneas totales  : {total_lineas}")
    total_clases = sum(len(i.clases) for i in archivos_info)
    total_funciones = sum(len(i.funciones) for i in archivos_info)
    total_metodos = sum(
        sum(len(c["metodos"]) for c in i.clases) for i in archivos_info
    )
    lineas.append(f"  Clases          : {total_clases}")
    lineas.append(f"  Funciones (top) : {total_funciones}")
    lineas.append(f"  Métodos (total) : {total_metodos}")
    lineas.append("")

    # ── Estructura del proyecto ──
    lineas.append(separador("ESTRUCTURA DEL PROYECTO"))
    lineas.append(arbol)
    lineas.append("")

    # ── Dependencias externas ──
    if deps_externas:
        lineas.append(separador("DEPENDENCIAS EXTERNAS (librerías de terceros)"))
        for lib, conteo_val in deps_externas.items():
            lineas.append(f"  • {lib}  (usado en {conteo_val} archivo(s))")
        lineas.append("")

    # ── Mapa de dependencias internas ──
    if deps_internas:
        lineas.append(separador("MAPA DE DEPENDENCIAS INTERNAS"))
        for archivo, deps in sorted(deps_internas.items()):
            lineas.append(f"  {archivo}")
            for dep in deps:
                lineas.append(f"    → {dep}")
        lineas.append("")

    # ── Detalle por archivo ──
    lineas.append(separador("DETALLE POR ARCHIVO"))

    # Agrupar archivos por directorio
    por_directorio: dict[str, list[InfoArchivo]] = defaultdict(list)
    for info in archivos_info:
        carpeta = os.path.dirname(info.ruta_relativa) or "."
        por_directorio[carpeta].append(info)

    for carpeta in sorted(por_directorio.keys()):
        lineas.append(f"\n{'─' * 72}")
        lineas.append(f"  📁 Directorio: {carpeta}/")
        lineas.append(f"{'─' * 72}")

        for info in sorted(por_directorio[carpeta], key=lambda x: x.ruta_relativa):
            lineas.append(f"\n  ▸ Archivo: {info.ruta_relativa}  ({info.lineas_totales} líneas)")
            lineas.append(f"  {'·' * 60}")

            if info.error_parseo:
                lineas.append(f"    ⚠ {info.error_parseo}")
                continue

            # Docstring del módulo
            if info.docstring_modulo:
                lineas.append("    Descripción del módulo:")
                for dl in info.docstring_modulo.splitlines():
                    lineas.append(f"      {dl}")

            # Imports
            if info.imports or info.imports_from:
                lineas.append("    Imports:")
                for imp in info.imports:
                    lineas.append(f"      import {imp}")
                for imp in info.imports_from:
                    lineas.append(f"      {imp}")

            # Constantes
            if info.constantes:
                lineas.append("    Constantes:")
                for c in info.constantes:
                    lineas.append(f"      {c}")

            # Variables globales
            if info.variables_globales:
                lineas.append("    Variables globales:")
                for v in info.variables_globales:
                    lineas.append(f"      {v}")

            # Funciones de nivel superior
            if info.funciones:
                lineas.append("    Funciones:")
                for func in info.funciones:
                    for dec in func["decoradores"]:
                        lineas.append(f"      {dec}")
                    lineas.append(f"      {func['firma']}  [línea {func['linea']}]")
                    if func["docstring"]:
                        for dl in func["docstring"].splitlines():
                            lineas.append(f"        \"\"\"{dl}\"\"\"")

            # Clases
            if info.clases:
                lineas.append("    Clases:")
                for cls in info.clases:
                    herencia = f"({', '.join(cls['bases'])})" if cls["bases"] else ""
                    for dec in cls["decoradores"]:
                        lineas.append(f"      {dec}")
                    lineas.append(f"      class {cls['nombre']}{herencia}  [línea {cls['linea']}]")

                    if cls["docstring"]:
                        for dl in cls["docstring"].splitlines():
                            lineas.append(f"        \"\"\"{dl}\"\"\"")

                    if cls["atributos_clase"]:
                        lineas.append("        Atributos de clase:")
                        for a in cls["atributos_clase"]:
                            lineas.append(f"          {a}")

                    if cls["atributos_init"]:
                        lineas.append("        Atributos de instancia (__init__):")
                        for a in cls["atributos_init"]:
                            lineas.append(f"          {a}")

                    if cls["metodos"]:
                        lineas.append("        Métodos:")
                        for met in cls["metodos"]:
                            for dec in met["decoradores"]:
                                lineas.append(f"          {dec}")
                            lineas.append(f"          {met['firma']}  [línea {met['linea']}]")
                            if met["docstring"]:
                                primera = met["docstring"].splitlines()[0]
                                lineas.append(f"            → {primera}")

    # ── Resumen ejecutivo ──
    lineas.append(separador("RESUMEN EJECUTIVO PARA AGENTE DE CÓDIGO"))
    lineas.append(textwrap.dedent("""\
    Este informe describe la estructura y los componentes del proyecto Python
    analizado. Cada sección proporciona información progresivamente más
    detallada:

    1. ESTRUCTURA DEL PROYECTO: Árbol de directorios y archivos .py
    2. DEPENDENCIAS EXTERNAS: Librerías de terceros necesarias
    3. MAPA DE DEPENDENCIAS INTERNAS: Qué módulo importa a cuál
    4. DETALLE POR ARCHIVO: Para cada .py se lista:
       - Docstring del módulo (si existe)
       - Imports (estándar, terceros e internos)
       - Constantes y variables globales relevantes
       - Funciones de nivel superior con su firma completa
       - Clases con:
         • Herencia y decoradores
         • Atributos de clase y de instancia
         • Todos los métodos con su firma

    Para solicitar modificaciones, indique el nombre del archivo y la clase
    o función a modificar. El agente podrá solicitar el fragmento de código
    específico necesario.
    """))

    lineas.append("=" * 72)
    lineas.append("  FIN DEL INFORME")
    lineas.append("=" * 72)

    return "\n".join(lineas)


# ─────────────────────────────────────────────────────────────
# PUNTO DE ENTRADA
# ─────────────────────────────────────────────────────────────

def main() -> None:
    raiz = os.path.dirname(os.path.abspath(__file__))
    ruta_informe = os.path.join(raiz, NOMBRE_INFORME)

    print(f"🔍 Analizando proyecto en: {raiz}")

    # 1. Descubrir archivos
    archivos_py = descubrir_archivos_py(raiz)
    if not archivos_py:
        print("⚠  No se encontraron archivos .py para analizar.")
        sys.exit(0)

    print(f"   Encontrados {len(archivos_py)} archivo(s) .py")

    # 2. Analizar cada archivo
    archivos_info: list[InfoArchivo] = []
    for ruta in archivos_py:
        rel = os.path.relpath(ruta, raiz)
        print(f"   Analizando: {rel}")
        info = InfoArchivo(ruta, rel)
        info.analizar()
        archivos_info.append(info)

    # 3. Generar árbol
    arbol = generar_arbol(raiz, archivos_py)

    # 4. Analizar dependencias
    deps_internas = analizar_dependencias_internas(archivos_info)
    deps_externas = analizar_dependencias_externas(archivos_info)

    # 5. Generar informe
    informe = formatear_informe(raiz, archivos_info, arbol, deps_internas, deps_externas)

    # 6. Escribir archivo
    with open(ruta_informe, "w", encoding="utf-8") as f:
        f.write(informe)

    print(f"\n✅ Informe generado: {ruta_informe}")
    print(f"   Tamaño: {os.path.getsize(ruta_informe):,} bytes")


if __name__ == "__main__":
    main()
