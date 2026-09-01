from pathlib import Path
import csv


SOURCE_ROOT = Path(
    r"C:\Users\igorm\Downloads\Mods Container Analisar\02_Extracted_LSLib"
)

OUTPUT_ROOT = Path(
    r"C:\Users\igorm\Downloads\Mods Container Analisar\03_Maps"
)

OUTPUT_FILE = OUTPUT_ROOT / "reference_architecture.csv"


def contains_path_part(path: Path, name: str) -> bool:
    """
    Verifica se uma parte específica existe no caminho,
    ignorando diferenças entre maiúsculas e minúsculas.
    """
    normalized_parts = [part.lower() for part in path.parts]

    return name.lower() in normalized_parts


def analyze_mod(mod_path: Path) -> dict:
    """
    Analisa estruturalmente uma referência extraída pela LSLib.
    """

    files = [
        path
        for path in mod_path.rglob("*")
        if path.is_file() and path.name != ".extracted.ok"
    ]

    return {
        "Mod": mod_path.name,

        # Quantidade total de arquivos reais encontrados
        "Files": len(files),

        # Manifestos do módulo
        "Meta": sum(
            path.name.lower() == "meta.lsx"
            for path in files
        ),

        # Arquivos encontrados dentro da camada RootTemplates
        "RootTemplates": sum(
            contains_path_part(path, "RootTemplates")
            for path in files
        ),

        # Scripts Lua
        "Lua": sum(
            path.suffix.lower() == ".lua"
            for path in files
        ),

        # Arquivos que pertencem à estrutura ScriptExtender
        "ScriptExtender": sum(
            contains_path_part(path, "ScriptExtender")
            for path in files
        ),

        # Arquivos relacionados ao MCM
        "MCM": sum(
            "mcm" in str(path).lower()
            for path in files
        ),

        # Arquivos localizados dentro da árvore Stats
        "Stats": sum(
            contains_path_part(path, "Stats")
            for path in files
        ),

        # Arquivos localizados dentro da árvore Localization
        "Localization": sum(
            contains_path_part(path, "Localization")
            for path in files
        ),
    }


def main() -> None:
    """
    Analisa todas as referências e gera um CSV comparativo.
    """

    if not SOURCE_ROOT.exists():
        raise FileNotFoundError(
            f"Pasta de referências não encontrada: {SOURCE_ROOT}"
        )

    OUTPUT_ROOT.mkdir(
        parents=True,
        exist_ok=True
    )

    mods = [
        path
        for path in SOURCE_ROOT.iterdir()
        if path.is_dir()
        and not path.name.startswith("_")
    ]

    # Mantém o relatório em ordem alfabética
    mods.sort(
        key=lambda path: path.name.lower()
    )

    results = [
        analyze_mod(mod)
        for mod in mods
    ]

    fieldnames = [
        "Mod",
        "Files",
        "Meta",
        "RootTemplates",
        "Lua",
        "ScriptExtender",
        "MCM",
        "Stats",
        "Localization",
    ]

    with OUTPUT_FILE.open(
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(results)

    print(
        f"[OK] Mods analisados: {len(results)}"
    )

    print(
        f"[OK] Relatório criado: {OUTPUT_FILE}"
    )

    # Diagnóstico adicional:
    # referências sem nenhum conteúdo real extraído.
    empty_mods = [
        result["Mod"]
        for result in results
        if result["Files"] == 0
    ]

    if empty_mods:
        print()
        print(
            "[WARN] Referências sem arquivos extraídos:"
        )

        for mod in empty_mods:
            print(
                f"       - {mod}"
            )


if __name__ == "__main__":
    main()