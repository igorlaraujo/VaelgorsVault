# Vaelgor's Vault - Custom Containers

**Vaelgor's Vault - Custom Containers** is a Baldur's Gate 3 mod by **Vaelgor**. It is currently under active development at version **0.1.0**.

## Current baseline

The first implemented family is Weapon Vaults separated by rarity: Common, Uncommon, Rare, Very Rare, and Legendary. Weapons acquired in a player inventory are automatically sorted into the matching Vault by runtime rarity.

Vault withdrawals are intentional: removing a weapon from a Vault to a player inventory prevents an immediate re-sort. Reinserting the weapon arms the behavior again, and this state persists through save/reload.

One-Handed Weapon Vault containers for the same five rarities are included in the current development package and await direct in-game validation. They do not add one-handed-specific autosort behavior.

## Dependency

The current mod core depends on Baldur's Gate 3 Script Extender Lua functionality. Current development observations are recorded in [Docs/STATE.md](Docs/STATE.md).

## Build

```powershell
python .\Tools\Build-VaelgorsVault.py --install
```

This project is not yet a release or compatibility claim. Current validated behavior, pending tests, and development constraints are documented in [Docs/STATE.md](Docs/STATE.md).
