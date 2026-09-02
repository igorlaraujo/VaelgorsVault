from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

DIVINE = Path(r"C:\Tools\BG3\LSLib\Packed\Tools\Divine.exe")

SRC = PROJECT_ROOT / "src"
BUILD = PROJECT_ROOT / "Build"
STAGING = BUILD / "Staging"

MOD_NAME = "VaelgorsVault_CustomContainers"

PAK_OUTPUT = BUILD / f"{MOD_NAME}.pak"

SRC_MODS = SRC / "Mods"
SRC_PUBLIC = SRC / "Public"
SRC_LOCALIZATION = SRC / "Localization"

STAGE_MODS = STAGING / "Mods"
STAGE_PUBLIC = STAGING / "Public"
STAGE_LOCALIZATION = STAGING / "Localization"

BG3_MODS = (
    Path.home()
    / "AppData"
    / "Local"
    / "Larian Studios"
    / "Baldur's Gate 3"
    / "Mods"
)

REQUIRED_PAK_PATHS = {
    f"Mods/{MOD_NAME}/meta.lsx",
    f"Public/{MOD_NAME}/RootTemplates/VV_WeaponVaults_Rarity.lsf",
    f"Public/{MOD_NAME}/RootTemplates/VV_WeaponVaults_ByType.lsf",
    f"Public/{MOD_NAME}/Stats/Generated/Data/Object.txt",
    f"Localization/English/{MOD_NAME}.loca",
}


def run_divine(*args: str) -> subprocess.CompletedProcess[str]:
    if not DIVINE.exists():
        raise FileNotFoundError(f"Divine.exe não encontrado: {DIVINE}")

    command = [
        str(DIVINE),
        "--game",
        "bg3",
        *args,
    ]

    print("\n>", " ".join(command))

    result = subprocess.run(
        command,
        text=True,
        capture_output=True,
        check=False,
    )

    if result.stdout:
        print(result.stdout.rstrip())

    if result.stderr:
        print(result.stderr.rstrip(), file=sys.stderr)

    if result.returncode != 0:
        raise RuntimeError(
            f"Divine falhou com código {result.returncode}"
        )

    return result


def clean_staging() -> None:
    print("[BUILD] Limpando staging")

    if STAGING.exists():
        shutil.rmtree(STAGING)

    STAGING.mkdir(parents=True, exist_ok=True)


def copy_sources() -> None:
    print("[BUILD] Copiando Mods e Public")

    shutil.copytree(SRC_MODS, STAGE_MODS)
    shutil.copytree(SRC_PUBLIC, STAGE_PUBLIC)


def compile_localization() -> None:
    print("[BUILD] Compilando Localization XML → LOCA")

    if not SRC_LOCALIZATION.exists():
        return

    for xml_file in SRC_LOCALIZATION.rglob("*.xml"):
        relative = xml_file.relative_to(SRC_LOCALIZATION)

        output = (
            STAGE_LOCALIZATION
            / relative.parent
            / f"{xml_file.stem}.loca"
        )

        output.parent.mkdir(parents=True, exist_ok=True)

        run_divine(
            "--action",
            "convert-loca",
            "--source",
            str(xml_file.resolve()),
            "--destination",
            str(output.resolve()),
        )

        if not output.exists():
            raise RuntimeError(
                f"Localization não foi criada: {output}"
            )


def compile_root_templates() -> None:
    print("[BUILD] Convertendo RootTemplates LSX → LSF")

    root_template_dirs = list(
        STAGE_PUBLIC.rglob("RootTemplates")
    )

    for root_dir in root_template_dirs:
        for lsx_file in list(root_dir.rglob("*.lsx")):
            lsf_file = lsx_file.with_suffix(".lsf")

            run_divine(
                "--action",
                "convert-resource",
                "--source",
                str(lsx_file.resolve()),
                "--destination",
                str(lsf_file.resolve()),
            )

            if not lsf_file.exists():
                raise RuntimeError(
                    f"LSF não criado: {lsf_file}"
                )

            lsx_file.unlink()

            print(
                f"[OK] {lsx_file.name} → {lsf_file.name}"
            )


def create_package() -> None:
    print("[BUILD] Criando PAK")

    BUILD.mkdir(parents=True, exist_ok=True)

    if PAK_OUTPUT.exists():
        PAK_OUTPUT.unlink()

    run_divine(
        "--action",
        "create-package",
        "--source",
        str(STAGING.resolve()),
        "--destination",
        str(PAK_OUTPUT.resolve()),
        "--compression-method",
        "lz4hc",
    )

    if not PAK_OUTPUT.exists():
        raise RuntimeError("PAK não foi criado.")

    print(f"[OK] PAK criado: {PAK_OUTPUT}")


def verify_package() -> None:
    print("[VERIFY] Validando conteúdo do PAK")

    result = run_divine(
        "--action",
        "list-package",
        "--source",
        str(PAK_OUTPUT.resolve()),
    )

    output = result.stdout.replace("\\", "/")

    missing = [
        required
        for required in REQUIRED_PAK_PATHS
        if required not in output
    ]

    if missing:
        print("\n[ERRO] Arquivos ausentes no PAK:")

        for item in missing:
            print(f"  - {item}")

        raise RuntimeError("Validação do PAK falhou.")

    if ".lsx" in "\n".join(
        line
        for line in output.splitlines()
        if "/RootTemplates/" in line
    ):
        raise RuntimeError(
            "RootTemplate LSX encontrado dentro do PAK."
        )

    print("[OK] Estrutura do PAK validada")


def install_package() -> None:
    print("[INSTALL] Instalando PAK")

    BG3_MODS.mkdir(parents=True, exist_ok=True)

    destination = BG3_MODS / PAK_OUTPUT.name

    shutil.copy2(PAK_OUTPUT, destination)

    print(f"[OK] Instalado em: {destination}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build do Vaelgor's Vault"
    )

    parser.add_argument(
        "--install",
        action="store_true",
        help="Copia o PAK final para a pasta Mods do BG3.",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    print("=== Vaelgor's Vault Build ===")

    clean_staging()
    copy_sources()
    compile_localization()
    compile_root_templates()
    create_package()
    verify_package()

    if args.install:
        install_package()

    print("\n[OK] Build concluído com sucesso.")


if __name__ == "__main__":
    main()
