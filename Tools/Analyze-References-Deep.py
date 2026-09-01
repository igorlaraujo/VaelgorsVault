from pathlib import Path
import csv
import re
import xml.etree.ElementTree as ET


SOURCE_ROOT = Path(
    r"C:\Users\igorm\Downloads\Mods Container Analisar\02_Extracted_LSLib"
)

OUTPUT_ROOT = Path(
    r"C:\Users\igorm\Downloads\Mods Container Analisar\03_Maps"
)

OUTPUT_FILE = OUTPUT_ROOT / "reference_deep_report.csv"


TEXT_EXTENSIONS = {
    ".lsx",
    ".txt",
    ".lua",
    ".json",
    ".xml",
    ".cfg",
    ".ini",
    ".md",
    ".xaml",
}


SIGNALS = {
    "AutoAddOnPickup": re.compile(
        r"\bContainerAutoAddOnPickup\b",
        re.IGNORECASE,
    ),
    "ContentFilter": re.compile(
        r"\bContainerContentFilterCondition\b",
        re.IGNORECASE,
    ),
    "TagCall": re.compile(
        r"\bTag\s*\(",
        re.IGNORECASE,
    ),
    "TreasureTable": re.compile(
        r"\bnew\s+treasuretable\b|\bTreasureTable\b",
        re.IGNORECASE,
    ),
    "Using": re.compile(
        r'^\s*using\s+"',
        re.IGNORECASE | re.MULTILINE,
    ),
    "NewEntry": re.compile(
        r'^\s*new\s+entry\s+"',
        re.IGNORECASE | re.MULTILINE,
    ),
    "BootstrapServer": re.compile(
        r"\bBootstrapServer\b",
        re.IGNORECASE,
    ),
    "BootstrapClient": re.compile(
        r"\bBootstrapClient\b",
        re.IGNORECASE,
    ),
    "MCM": re.compile(
        r"\bMCM\b|ModConfigMenu|Mod Configuration Menu",
        re.IGNORECASE,
    ),
    "Rename": re.compile(
        r"\brename\b|\bSetName\b|\bDisplayName\b",
        re.IGNORECASE,
    ),
    "RootTemplateReference": re.compile(
        r"\bRootTemplate\b",
        re.IGNORECASE,
    ),
}


def contains_path_part(path: Path, name: str) -> bool:
    return name.lower() in (
        part.lower()
        for part in path.parts
    )


def read_text_safely(path: Path) -> str:
    try:
        return path.read_text(
            encoding="utf-8-sig",
            errors="ignore",
        )
    except OSError:
        return ""


def parse_meta(meta_path: Path) -> dict:
    result = {
        "Name": "",
        "Author": "",
        "Folder": "",
        "UUID": "",
        "Version64": "",
        "Dependencies": "",
    }

    try:
        tree = ET.parse(meta_path)
        root = tree.getroot()
    except (ET.ParseError, OSError):
        return result

    module_info = root.find(
        ".//node[@id='ModuleInfo']"
    )

    if module_info is not None:
        attributes = {
            attribute.get("id"): attribute.get("value", "")
            for attribute
            in module_info.findall("./attribute")
        }

        for key in (
            "Name",
            "Author",
            "Folder",
            "UUID",
            "Version64",
        ):
            result[key] = attributes.get(key, "")

    dependencies_node = root.find(
        ".//node[@id='Dependencies']"
    )

    dependencies = []

    if dependencies_node is not None:
        for dependency_node in dependencies_node.findall(
            ".//node"
        ):
            attributes = {
                attribute.get("id"): attribute.get(
                    "value",
                    "",
                )
                for attribute
                in dependency_node.findall("./attribute")
            }

            if not attributes:
                continue

            name = (
                attributes.get("Name")
                or attributes.get("Folder")
                or "Unnamed"
            )

            uuid = attributes.get("UUID", "")

            if uuid:
                dependencies.append(
                    f"{name} [{uuid}]"
                )
            else:
                dependencies.append(name)

    result["Dependencies"] = "; ".join(
        dependencies
    )

    return result


def classify_architecture(
    roottemplates: int,
    stats: int,
    lua: int,
    script_extender: int,
    mcm: int,
    ui: int,
) -> str:

    has_data = (
        roottemplates > 0
        or stats > 0
    )

    has_runtime = (
        lua > 0
        or script_extender > 0
        or mcm > 0
    )

    if has_data and has_runtime:
        return "HYBRID"

    if has_runtime:
        return "RUNTIME / SCRIPT EXTENDER"

    if has_data:
        return "DATA-DRIVEN"

    if ui > 0:
        return "UI / OTHER"

    return "NEEDS REVIEW"


def analyze_mod(mod_path: Path) -> dict:
    files = [
        path
        for path in mod_path.rglob("*")
        if path.is_file()
        and path.name != ".extracted.ok"
    ]

    text_files = [
        path
        for path in files
        if path.suffix.lower()
        in TEXT_EXTENSIONS
    ]

    roottemplate_lsx = [
        path
        for path in files
        if path.suffix.lower() == ".lsx"
        and contains_path_part(
            path,
            "RootTemplates",
        )
    ]

    roottemplate_lsf = [
        path
        for path in files
        if path.suffix.lower() == ".lsf"
        and contains_path_part(
            path,
            "RootTemplates",
        )
    ]

    stats_files = [
        path
        for path in files
        if path.suffix.lower() == ".txt"
        and contains_path_part(
            path,
            "Stats",
        )
    ]

    tag_files = [
        path
        for path in files
        if path.suffix.lower() == ".lsx"
        and contains_path_part(
            path,
            "Tags",
        )
    ]

    lua_files = [
        path
        for path in files
        if path.suffix.lower() == ".lua"
    ]

    script_extender_files = [
        path
        for path in files
        if contains_path_part(
            path,
            "ScriptExtender",
        )
    ]

    mcm_path_files = [
        path
        for path in files
        if "mcm" in str(path).lower()
    ]

    localization_files = [
        path
        for path in files
        if contains_path_part(
            path,
            "Localization",
        )
        or path.suffix.lower() == ".loca"
    ]

    levels_files = [
        path
        for path in files
        if contains_path_part(
            path,
            "Levels",
        )
    ]

    ui_files = [
        path
        for path in files
        if path.suffix.lower()
        in {
            ".xaml",
            ".swf",
            ".gfx",
        }
    ]

    meta_files = [
        path
        for path in files
        if path.name.lower() == "meta.lsx"
    ]

    signal_counts = {
        signal: 0
        for signal in SIGNALS
    }

    key_files = {}

    for path in text_files:
        text = read_text_safely(path)

        if not text:
            continue

        relative_path = str(
            path.relative_to(mod_path)
        )

        reasons = set()

        for signal_name, pattern in SIGNALS.items():
            matches = pattern.findall(text)

            if matches:
                signal_counts[signal_name] += len(
                    matches
                )
                reasons.add(signal_name)

        lower_path = relative_path.lower()

        if path.name.lower() == "meta.lsx":
            reasons.add("Manifest")

        if "scriptextender" in lower_path:
            reasons.add("ScriptExtender")

        if path.suffix.lower() == ".lua":
            reasons.add("Lua")

        if "mcm" in lower_path:
            reasons.add("MCM")

        if "roottemplates" in lower_path:
            reasons.add("RootTemplates")

        if "stats" in lower_path:
            reasons.add("Stats")

        if "levels" in lower_path:
            reasons.add("Levels")

        if reasons:
            key_files[relative_path] = reasons

    manifests = [
        parse_meta(path)
        for path in meta_files
    ]

    manifest_names = "; ".join(
        manifest["Name"]
        for manifest in manifests
        if manifest["Name"]
    )

    manifest_authors = "; ".join(
        manifest["Author"]
        for manifest in manifests
        if manifest["Author"]
    )

    manifest_folders = "; ".join(
        manifest["Folder"]
        for manifest in manifests
        if manifest["Folder"]
    )

    manifest_uuids = "; ".join(
        manifest["UUID"]
        for manifest in manifests
        if manifest["UUID"]
    )

    manifest_versions = "; ".join(
        manifest["Version64"]
        for manifest in manifests
        if manifest["Version64"]
    )

    dependencies = "; ".join(
        manifest["Dependencies"]
        for manifest in manifests
        if manifest["Dependencies"]
    )

    def key_file_score(item) -> tuple:
        path_string, reasons = item

        priority = 10

        lower = path_string.lower()

        if lower.endswith("meta.lsx"):
            priority = 0
        elif lower.endswith(".lua"):
            priority = 1
        elif "scriptextender" in lower:
            priority = 2
        elif "mcm" in lower:
            priority = 3
        elif "roottemplates" in lower:
            priority = 4
        elif "stats" in lower:
            priority = 5
        elif "levels" in lower:
            priority = 6

        return (
            priority,
            -len(reasons),
            path_string.lower(),
        )

    sorted_key_files = sorted(
        key_files.items(),
        key=key_file_score,
    )

    selected_key_files = [
        (
            f"{path} "
            f"[{', '.join(sorted(reasons))}]"
        )
        for path, reasons
        in sorted_key_files[:15]
    ]

    architecture = classify_architecture(
        roottemplates=len(roottemplate_lsx),
        stats=len(stats_files),
        lua=len(lua_files),
        script_extender=len(
            script_extender_files
        ),
        mcm=len(mcm_path_files),
        ui=len(ui_files),
    )

    return {
        "Reference": mod_path.name,
        "Architecture": architecture,

        "ManifestName": manifest_names,
        "Author": manifest_authors,
        "Folder": manifest_folders,
        "UUID": manifest_uuids,
        "Version64": manifest_versions,
        "Dependencies": dependencies,

        "Files": len(files),
        "TextFiles": len(text_files),

        "RootTemplatesLSX": len(
            roottemplate_lsx
        ),
        "RootTemplatesLSF": len(
            roottemplate_lsf
        ),
        "StatsTXT": len(stats_files),
        "TagDefinitions": len(tag_files),

        "Lua": len(lua_files),
        "ScriptExtenderFiles": len(
            script_extender_files
        ),
        "MCMPathFiles": len(
            mcm_path_files
        ),

        "LocalizationFiles": len(
            localization_files
        ),
        "LevelsFiles": len(levels_files),
        "UIFiles": len(ui_files),

        "AutoAddSignals": signal_counts[
            "AutoAddOnPickup"
        ],
        "ContentFilterSignals": signal_counts[
            "ContentFilter"
        ],
        "TagCalls": signal_counts[
            "TagCall"
        ],
        "TreasureTableSignals": signal_counts[
            "TreasureTable"
        ],
        "UsingStatements": signal_counts[
            "Using"
        ],
        "NewEntryStatements": signal_counts[
            "NewEntry"
        ],
        "BootstrapServerSignals": signal_counts[
            "BootstrapServer"
        ],
        "BootstrapClientSignals": signal_counts[
            "BootstrapClient"
        ],
        "MCMSignals": signal_counts[
            "MCM"
        ],
        "RenameNameSignals": signal_counts[
            "Rename"
        ],
        "RootTemplateReferences": signal_counts[
            "RootTemplateReference"
        ],

        "KeyFiles": " | ".join(
            selected_key_files
        ),
    }


def main() -> None:
    if not SOURCE_ROOT.exists():
        raise FileNotFoundError(
            f"Pasta não encontrada: {SOURCE_ROOT}"
        )

    OUTPUT_ROOT.mkdir(
        parents=True,
        exist_ok=True,
    )

    mods = sorted(
        (
            path
            for path in SOURCE_ROOT.iterdir()
            if path.is_dir()
            and not path.name.startswith("_")
        ),
        key=lambda path: path.name.lower(),
    )

    results = [
        analyze_mod(mod)
        for mod in mods
    ]

    if not results:
        raise RuntimeError(
            "Nenhuma referência encontrada."
        )

    fieldnames = list(
        results[0].keys()
    )

    with OUTPUT_FILE.open(
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()
        writer.writerows(results)

    print(
        f"[OK] Referências analisadas: "
        f"{len(results)}"
    )

    print(
        f"[OK] Relatório: {OUTPUT_FILE}"
    )

    print()
    print("[ARQUITETURAS]")

    architecture_counts = {}

    for result in results:
        architecture = result[
            "Architecture"
        ]

        architecture_counts[architecture] = (
            architecture_counts.get(
                architecture,
                0,
            )
            + 1
        )

    for architecture, count in sorted(
        architecture_counts.items()
    ):
        print(
            f"  {architecture}: {count}"
        )


if __name__ == "__main__":
    main()