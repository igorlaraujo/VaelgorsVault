# Changelog

## 0.1.0 - Development baseline

### Added

- Five Weapon Vault containers for Common, Uncommon, Rare, Very Rare, and Legendary weapons.
- Rarity-based inventory autosort for the validated Common, Rare, Very Rare, and Legendary mappings.
- Persistent manual-withdrawal handling to prevent immediate re-sorting after a Vault-to-inventory withdrawal.
- Weapon Vault Object Stats, English localization, and Tutorial Chest delivery for all five Vaults.
- Build pipeline support for XML-to-LOCA, LSX-to-LSF, PAK creation, and package-path validation.
- Five One-Handed Weapon Vault containers, with Object Stats, English localization, and Tutorial Chest categories.
- Fifteen ByType Vault containers for Two-Handed Weapons, Ranged Weapons, and Daggers, each across the five existing rarities.
- Type × Rarity autosort with Core Rarity fallback for unavailable Stats, classification, or matching ByType Vaults.

### Changed

- Split Weapon Vault RootTemplates into `VV_WeaponVaults_Rarity.lsx` and `VV_WeaponVaults_ByType.lsx` without changing runtime logic, UUIDs, handles, or container data.

### Confirmed

- Type × Rarity autosort passes in-game for Daggers, Ranged, Two-Handed, and One-Handed weapons across runtime rarities `0` through `4`.
- `Take All`, Core Rarity fallback, and manual withdrawal pass with the ByType routing.
- `Kingsknife` currently resolves as `unknown` and safely falls back to Core Rarity; its Stats classification remains a pending edge case.

### Known pending validation

- Interaction with the existing inventory reorganization hotkey.
- Kingsknife Stats classification before any classifier change.
