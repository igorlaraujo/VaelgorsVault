# STATE.md — Vaelgor's Vault - Custom Containers

> Mutable technical state for development.  
> Update this file whenever implementation, tests, versions, UUIDs, known issues or next actions change.

## 1. Identity

- Module Name: **Vaelgor's Vault - Custom Containers**
- Module Folder: `VaelgorsVault_CustomContainers`
- Module UUID: `e3e24e7e-6e34-4b06-93a5-c2368607a387`
- Development Version: `0.1.0`
- Version64 previously used: `140737488355328`
- Public author/modder identity: **Vaelgor**

## 2. Current environment

### BG3 / Script Extender observed during current test session

- BG3 Script Extender: **BG3Ext v32**
- Build date shown by console: **Jun 21 2026**
- Game version shown by console: **v4.72.9.685**
- Module config accepted by SE:
  - RequiredVersion: `12`
  - Feature flag: `Lua`

These values are current development observations, not permanent release requirements.

### Development tooling

- Windows
- PyCharm
- PowerShell
- LSLib/Divine:
  `C:\Tools\BG3\LSLib\Packed\Tools\Divine.exe`

### Python environments observed

PowerShell currently resolves:

```text
C:\Python314\python.exe
Python 3.14.7
```

The project `.venv` points to an older Python 3.12.10 installation that is no longer available:

```text
C:\Users\igorm\AppData\Local\Programs\Python\Python312\python.exe
```

Therefore the `.venv` is currently broken.

The Vaelgor build pipeline has been successfully executed using the global Python 3.14.7 resolved by PowerShell.

Do not repair/recreate the `.venv` while diagnosing unrelated mod behavior.

### Current build command

```powershell
python .\Tools\Build-VaelgorsVault.py --install
```

## 3. Project structure

Current relevant structure:

```text
VaelgorsVault/
├── Build/
├── Docs/
│   └── STATE.md
├── References/
├── src/
│   ├── Localization/
│   │   ├── English/
│   │   │   └── VaelgorsVault_CustomContainers.xml
│   │   └── PT-BR/
│   ├── Mods/
│   │   └── VaelgorsVault_CustomContainers/
│   │       ├── meta.lsx
│   │       └── ScriptExtender/
│   │           ├── Config.json
│   │           └── Lua/
│   │               └── BootstrapServer.lua
│   └── Public/
│       └── VaelgorsVault_CustomContainers/
│           ├── RootTemplates/
│           │   ├── VV_WeaponVaults_Rarity.lsx
│           │   └── VV_WeaponVaults_ByType.lsx
│           └── Stats/
│               └── Generated/
│                   ├── Data/
│                   │   └── Object.txt
│                   └── TreasureTable.txt
├── Tools/
│   ├── Analyze-References.py
│   ├── Analyze-References-Deep.py
│   ├── Build-VaelgorsVault.py
│   ├── Extract-ReferenceArchives.ps1
│   └── Extract-ReferencePaks.ps1
├── AGENTS.md
├── CHANGELOG.md
├── README.md
└── .gitignore
```

Current accidental npm artifacts may still exist locally:

```text
node_modules/
package.json
package-lock.json
```

They are unrelated to Vaelgor's Vault and must not become part of the project repository.

## 4. Build pipeline status

### Confirmed working

The Python build pipeline currently:

1. cleans `Build\Staging`;
2. copies `src\Mods`;
3. copies `src\Public`;
4. converts Localization XML → LOCA;
5. converts RootTemplate LSX → LSF;
6. removes staging RootTemplate LSX;
7. creates the PAK with LZ4HC;
8. verifies required package paths;
9. optionally installs the generated PAK.

### Important historical fix

Initial RootTemplate packaging used `.lsx` directly and failed runtime lookup:

```lua
Ext.Template.GetTemplate(UUID)
```

returned `nil`.

After converting LSX → LSF during the build, the template loaded and spawned correctly.

### Current PAK verification

Using:

```powershell
& "C:\Tools\BG3\LSLib\Packed\Tools\Divine.exe" `
    -a list-package `
    -g bg3 `
    -s $pak |
    Select-String "TreasureTable|Object.txt|VV_WeaponVaults"
```

confirmed that the PAK contains:

```text
Localization/English/VaelgorsVault_CustomContainers.loca
Public/VaelgorsVault_CustomContainers/RootTemplates/VV_WeaponVaults_Rarity.lsf
Public/VaelgorsVault_CustomContainers/RootTemplates/VV_WeaponVaults_ByType.lsf
Public/VaelgorsVault_CustomContainers/Stats/Generated/Data/Object.txt
Public/VaelgorsVault_CustomContainers/Stats/Generated/TreasureTable.txt
```

The generated/staged `Object.txt` was also verified to contain exactly one definition of each:

```text
OBJ_VV_Weapons_Common
OBJ_VV_Weapons_Uncommon
OBJ_VV_Weapons_Rare
OBJ_VV_Weapons_VeryRare
OBJ_VV_Weapons_Legendary
```

### Codex restricted-execution observation

When the pipeline was executed from a restricted Codex execution context, the build and PAK validation succeeded but the final `--install` step raised:

```text
FileExistsError: [WinError 183]
```

for:

```text
C:\Users\igorm\AppData\Local\Larian Studios\Baldur's Gate 3\Mods
```

Direct inspection confirmed that this path exists and is a valid directory.

The build script already correctly uses:

```python
BG3_MODS.mkdir(parents=True, exist_ok=True)
```

No pipeline code change was made.

The failure is currently classified as an execution-context limitation, not a confirmed build-script bug.

Manual PAK copying remains a valid fallback when running builds from restricted agent contexts.

## 5. Weapon Vault architecture

### RootTemplate files

The Weapon Vault family is organized into a stable core and a type extension:

```text
RootTemplates/
├── VV_WeaponVaults_Rarity.lsx
│   ├── Common
│   ├── Uncommon
│   ├── Rare
│   ├── Very Rare
│   └── Legendary
└── VV_WeaponVaults_ByType.lsx
    ├── One-Handed Common
    ├── One-Handed Uncommon
    ├── One-Handed Rare
    ├── One-Handed Very Rare
    └── One-Handed Legendary
```

The build recursively converts both source files to `VV_WeaponVaults_Rarity.lsf` and `VV_WeaponVaults_ByType.lsf`. The generated PAK contains both LSF files; no LSX is retained in its RootTemplates directory.

`Object.txt`, `TreasureTable.txt`, and the English localization XML remain unified. The build copies/compiles files recursively, but runtime merging of multiple Stats, TreasureTable, or LOCA files has not been directly validated for this module.

### Shared ParentTemplate

Verified vanilla ParentTemplate used by current Weapon Vaults:

```text
0e600db2-aa76-4c98-b4d5-a55c0853e7f1
```

Vanilla object:

```text
CONT_GEN_Chest_Rich_B
```

Observed properties:

- Icon: `Item_CONT_GEN_Chest_Rich_B`
- Stats: `OBJ_Chest_Wood`
- Type: `item`
- VisualTemplate: `39898e5b-3534-ad58-7ba6-279ec7c482b8`
- Parent: `d91b10a4-b196-415d-963c-f8e90fc4eb47`

The vanilla template had an `InventoryList` containing `Exploration_Major`, so Vaelgor Vault templates explicitly override their inventory list to `Empty`.

Inherited `OnDestroyActions` have not yet been altered.

## 6. Weapon Vault identities

### Common Weapon Vault

- Name: `VV_Weapons_Common`
- Stats: `OBJ_VV_Weapons_Common`
- RootTemplate UUID: `92f192d9-e70f-44b0-9d6a-a00ecbe8ca17`

### Uncommon Weapon Vault

- Name: `VV_Weapons_Uncommon`
- Stats: `OBJ_VV_Weapons_Uncommon`
- RootTemplate UUID: `0bfcd877-4dac-4829-a9f7-72fecaad9643`

### Rare Weapon Vault

- Name: `VV_Weapons_Rare`
- Stats: `OBJ_VV_Weapons_Rare`
- RootTemplate UUID: `70fbde6f-a5bb-4305-a522-08f97ee6941b`

Original validated English localization handles:

- DisplayName: `h271ab5c4g6fceg43c1ga91bg9d6759320d13`
- Description: `h436e4897ga14dg4be7g8447g17c80da9cddc`
- TechnicalDescription: `h9c0905ecg7100g417bg99e3gdaf87d56e30e`

Current English text:

- `Rare Weapon Vault`
- `A reinforced vault designed for the secure storage of rare weapons.`
- `Stores rare weapons.`

### Very Rare Weapon Vault

- Name: `VV_Weapons_VeryRare`
- Stats: `OBJ_VV_Weapons_VeryRare`
- RootTemplate UUID: `25ea810a-1651-48ff-bf81-5e87c25276cd`

### Legendary Weapon Vault

- Name: `VV_Weapons_Legendary`
- Stats: `OBJ_VV_Weapons_Legendary`
- RootTemplate UUID: `36d997e4-7b9e-4117-803c-61d39c5fa72d`

### One-Handed Weapon Vaults

The following RootTemplates, Object Stats, English localization entries, and Tutorial Chest categories are build-validated but still need direct in-game testing:

- Common: `VV_OneHandedWeapons_Common` / `OBJ_VV_OneHandedWeapons_Common` / `4b7da40d-596b-42d4-be19-9e1aa13fded0`
- Uncommon: `VV_OneHandedWeapons_Uncommon` / `OBJ_VV_OneHandedWeapons_Uncommon` / `c304459c-f469-43ea-b40f-6090be22f25d`
- Rare: `VV_OneHandedWeapons_Rare` / `OBJ_VV_OneHandedWeapons_Rare` / `0947a3b8-5b1e-48e2-a7e2-339131b25890`
- Very Rare: `VV_OneHandedWeapons_VeryRare` / `OBJ_VV_OneHandedWeapons_VeryRare` / `699486a3-d436-48b2-9fd5-bb469fa59761`
- Legendary: `VV_OneHandedWeapons_Legendary` / `OBJ_VV_OneHandedWeapons_Legendary` / `d53ded6c-cd58-4040-b494-4df9e1c8656f`

The runtime sorter routes One-Handed weapons through the ByType family at the matching runtime rarity. This routing is PASS in-game for rarities `0` through `4`.

### Additional ByType Weapon Vaults

The following Two-Handed, Ranged, and Dagger Vaults are delivered through the Tutorial Chest. The runtime sorter selects the matching ByType Vault at each runtime rarity; this routing is PASS in-game for rarities `0` through `4`.

| Family | Common | Uncommon | Rare | Very Rare | Legendary |
|---|---|---|---|---|---|
| Two-Handed | `fd7780b2-cd2b-4271-af6b-a992c170db1f` | `18900e0d-e5b9-4d91-a74c-28d953e89283` | `15f0f8f5-9425-476f-aab4-50d14f3c2c66` | `a2c544d1-9e25-4300-a522-cf04943f5353` | `0e86d258-6675-4dd3-81dd-0d6de751e10f` |
| Ranged | `aa474431-2cde-4959-a7c1-069dffdeb469` | `30c376fe-c0d7-4a40-af0a-9567c010d3b9` | `4a81581f-d186-443a-a190-de6e7cb004ea` | `42e7356f-7396-490c-a0ba-c9ed9ff87ce0` | `73d1ebb3-8579-4a91-b782-a1bbfc08e4c0` |
| Daggers | `e2be7ca4-5e99-43a3-9d4b-e0a55da22fa6` | `2b45683c-01c3-47b4-a47a-6d1729d56b7b` | `873a2cd0-9952-41b5-b0d2-0e85947bbce5` | `6ee8e987-ebc4-467f-b2d4-8886aa960f4c` | `e6a8e362-3647-43dd-aa3f-b430d29e0423` |

## 7. Stats definitions

`Object.txt` currently defines ten Object Stats entries: the five original Weapon Vault entries and five One-Handed Weapon Vault entries.

```text
OBJ_VV_Weapons_Common
OBJ_VV_Weapons_Uncommon
OBJ_VV_Weapons_Rare
OBJ_VV_Weapons_VeryRare
OBJ_VV_Weapons_Legendary
```

Each currently:

- `type "Object"`
- `using "OBJ_Chest_Wood"`
- own RootTemplate UUID
- `Weight = 1`
- `Vitality = -1`

### Historical issue

During development, `Object.txt` was accidentally replaced by localization-handle notes and temporarily lost all five Object Stats definitions.

A Codex read-only audit detected the inconsistency between the actual source files and `STATE.md`.

`Object.txt` was restored to the five validated `OBJ_VV_Weapons_*` definitions before the successful Tutorial Chest/localization test.

The corrected definitions were verified both in staging and in the generated PAK.

### Current file organization

The twenty-five Object Stats remain in one `Object.txt`. They are not split by Core Rarity/ByType until multi-file Stats loading is directly verified in-game.

## 8. Runtime rarity mapping

Runtime lookup:

```lua
Ext.Entity.Get(item).Value.Rarity
```

### Directly confirmed in-game

| Runtime value | Rarity | Status |
|---:|---|---|
| `0` | Common | PASS |
| `1` | Uncommon | PASS |
| `2` | Rare | PASS |
| `3` | Very Rare | PASS |
| `4` | Legendary | PASS |

All runtime values from `0` through `4` are directly confirmed in-game.

## 9. Autosort implementation

### Event

Current sorter uses:

```lua
Ext.Osiris.RegisterListener("TemplateAddedTo", 4, "after", ...)
```

### Weapon detection

Uses:

```lua
Osi.IsWeapon(object)
```

### Direct owner filter

Uses:

```lua
Osi.GetDirectInventoryOwner(object)
```

The sorter only routes when the direct owner is a player.

This prevents simple recursive self-sorting when an item is already directly inside a Vaelgor Vault.

### Target lookup

For each rarity, the Lua table stores:

- display/log name;
- RootTemplate UUID;
- runtime template string.

Target Vault is found with:

```lua
Osi.GetItemByTemplateInInventory(
    targetVault.RootTemplate,
    directOwner
)
```

### Movement

Uses:

```lua
Osi.ToInventory(
    object,
    vault,
    1,
    0,
    0
)
```

### Type × Rarity routing

The sorter reads `Osi.GetStatString(item)` and checks the resolved weapon Stats entry after determining its runtime rarity. Classification priority is:

1. `Proficiency Group` contains `Daggers`;
2. `Slot` equals `Ranged Main Weapon`;
3. `Weapon Properties` contains `Twohanded`;
4. `Slot` equals `Melee Main Weapon` or `Melee Offhand Weapon` for One-Handed;
5. otherwise, no type is resolved.

Each class routes to its matching ByType Vault at the same rarity. If the Stats entry, any required classifier, or the specific ByType Vault cannot be resolved, the existing Core Rarity Vault remains the fallback. Runtime routing is PASS for Daggers, Ranged, Two-Handed, and One-Handed weapons across rarities `0` through `4`.

`Take All`, Core fallback, and the manual-withdrawal state are PASS with this routing. The manual withdrawal state recognizes Core and ByType Vault runtime templates.

### Pending edge case

`Kingsknife` currently resolves as `unknown` and routes to the matching Core Rarity Vault. This is an expected safe fallback, but its Stats classification requires later inspection before any classifier change.

### Current scope

The sorter currently handles **inventory organization only**.

It does not implement:

- world pickup;
- aura collection;
- corpse scanning;
- remote pickup;
- world-container harvesting.

World collection remains a possible later/optional concern and must not be mixed into the current baseline without a deliberate design decision.

## 10. Manual withdrawal system

### Problem originally observed

Initial autosort implementation trapped Rare weapons inside the Vault:

```text
Vault → player inventory
→ TemplateAddedTo
→ sorter interpreted withdrawal as acquisition
→ weapon immediately returned to Vault
```

Equipping and then returning to inventory behaved differently, proving that UI inventory movement could not be distinguished using the initial listener data alone.

### Diagnostic events tested

Temporary listeners were tested for:

- `MovedFromTo`
- `RemovedFrom`
- `Equipped`
- `Unequipped`

They did not provide useful event data for the specific inventory flow being diagnosed and were removed from the active implementation.

### Current solution

Persistent per-weapon UserVariable:

```lua
VV_WeaponState
```

Current registration is server-side only and persistent.

The initial attempt enabled client synchronization and produced:

```text
Tried to sync variable 'VV_WeaponState' that has no prototype!
```

Removing unnecessary client synchronization fixed the warning.

### Current behavior

When a weapon enters any Vaelgor Weapon Vault:

- `ManualWithdrawalReady = true`

When that weapon later enters player inventory:

- if the flag is true, the sorter consumes the flag;
- manual withdrawal is allowed;
- the weapon is not immediately re-sorted.

Reinserting the weapon into a Vault re-arms the state.

### Persistence

Confirmed:

- weapon remains inside Vault after save/reload;
- persistent withdrawal state survives save/reload;
- after reload, direct manual withdrawal to inventory still works.

## 11. Accepted drop behavior

Current observed/accepted behavior:

### Flow A

```text
Vault
→ Inventory
→ Ground
→ pickup
```

Result:

- pickup is treated as a new acquisition;
- weapon autosorts back into the appropriate Vault.

### Flow B

```text
Vault
→ Ground directly
→ pickup
```

Result:

- withdrawal intent remains armed;
- pickup returns the weapon to player inventory;
- it remains outside the Vault.

Current decision:

**Accepted behavior; not a bug unless later UX testing shows a real problem.**

## 12. Tests completed

### Test 01 — Physical container persistence

**PASS**

- Rare Weapon Vault spawns physically.
- Starts empty.
- Accepts items.
- Vault and contents persist through save/reload.

### Test 02 — Weapon detection

**PASS**

- `Osi.IsWeapon` reliably identifies tested weapons.

### Test 03 — Runtime rarity detection

**PASS for 0, 2, 3, 4**

- Common = `0`
- Rare = `2`
- Very Rare = `3`
- Legendary = `4`

Uncommon = `1` is now directly validated in-game.

### Test 04 — Rare autosort

**PASS**

- Rare weapon entering player inventory routes to Rare Weapon Vault.
- Common, Very Rare and Legendary did not incorrectly route to Rare.

### Test 05 — Initial manual withdrawal

**FAIL**

- direct Vault → Inventory caused immediate re-sort.

Historical failure retained for traceability.

### Test 06 — Manual withdrawal corrected

**PASS**

- direct Vault → Inventory remains outside;
- reinsert → withdraw again remains outside;
- no UserVariable sync warning after server-only configuration.

### Test 07 — Manual withdrawal persistence

**PASS**

- weapon stored in Vault;
- save;
- reload;
- manual withdrawal still works.

### Test 08 — Multi-GameObject RootTemplate baseline (historical)

**PASS**

- the former `VV_WeaponVaults.lsx` containing five original `GameObjects` converted successfully;
- all five templates can be spawned by UUID;
- retained as the pre-Core-Rarity/ByType baseline.

### Test 12 — Core Rarity + ByType RootTemplate build

**PASS (package structure)**

- `VV_WeaponVaults_Rarity.lsx` and `VV_WeaponVaults_ByType.lsx` each convert to LSF;
- the generated PAK contains both LSF files and no RootTemplate LSX;
- original UUIDs, Object Stats names, and localization handles remain unchanged by static verification.

In-game loading of the split RootTemplates remains pending.

### Test 09 — Type × Rarity autosort

**PASS**

Directly confirmed in-game:

- Daggers, Ranged, Two-Handed, and One-Handed weapons route to the matching ByType Vault;
- runtime rarities `0` through `4` route to their matching rarity;
- `Take All` works with the sorter;
- unresolved classification or unavailable matching ByType Vault falls back to Core Rarity;
- manual withdrawal remains functional with Core and ByType Vaults.

Pending edge case:

- `Kingsknife` → `unknown` → Core Rarity fallback; inspect its Stats before changing classifiers.

### Test 10 — Tutorial Chest delivery

**PASS**

- a newly summoned Tutorial Chest contains all five Weapon Vaults;
- Common, Uncommon, Rare, Very Rare and Legendary Weapon Vaults are delivered correctly;
- Tutorial Chest Summoning remains a development/test fixture, not a declared dependency.

### Test 11 — Weapon Vault localization

**PASS**

- Common Weapon Vault displays the correct name and descriptions;
- Uncommon Weapon Vault displays the correct name and descriptions;
- Rare Weapon Vault remains correct;
- Very Rare Weapon Vault displays the correct name and descriptions;
- Legendary Weapon Vault displays the correct name and descriptions;
- previous `Not Found` issue is resolved.

## 13. Current logging behavior

The following message is often emitted twice when a weapon enters a Vault:

```text
<rarity> weapon stored; manual withdrawal armed
```

Current assessment:

- event/log duplication;
- functionally idempotent (`true → true`);
- no confirmed gameplay regression.

Decision:

**Do not fix until it causes a real problem or logging cleanup becomes worthwhile.**

## 14. Tutorial Chest integration

### Goal

Use Tutorial Chest as a development/distribution fixture so all Vaults can be obtained without manual UUID spawning.

### Current file

```text
src\Public\VaelgorsVault_CustomContainers\Stats\Generated\TreasureTable.txt
```

Current target:

```text
TUT_Chest_Potions
```

### Reference verification

The Tutorial Chest Summoning reference mod was inspected.

Observed architecture:

- summons a new Tutorial Chest RootTemplate;
- summoned chest uses `InventoryList = TUT_Chest_Potions`.

The Evelyn Dagger reference mod was also inspected.

Its working TreasureTable pattern uses:

```text
treasure itemtypes "Common","Uncommon","Rare","Epic","Legendary","Divine","Unique"

new treasuretable "TUT_Chest_Potions"
CanMerge 1
...
```

The Vaelgor TreasureTable was aligned with this working structure.

### Current validated structure

```text
treasure itemtypes "Common","Uncommon","Rare","Epic","Legendary","Divine","Unique"

new treasuretable "TUT_Chest_Potions"
CanMerge 1

new subtable "1,1"
object category "I_OBJ_VV_Weapons_Common",1,0,0,0,0,0,0,0

new subtable "1,1"
object category "I_OBJ_VV_Weapons_Uncommon",1,0,0,0,0,0,0,0

new subtable "1,1"
object category "I_OBJ_VV_Weapons_Rare",1,0,0,0,0,0,0,0

new subtable "1,1"
object category "I_OBJ_VV_Weapons_VeryRare",1,0,0,0,0,0,0,0

new subtable "1,1"
object category "I_OBJ_VV_Weapons_Legendary",1,0,0,0,0,0,0,0
```

### Status

**PASS**

A newly summoned Tutorial Chest correctly contains:

- Common Weapon Vault;
- Uncommon Weapon Vault;
- Rare Weapon Vault;
- Very Rare Weapon Vault;
- Legendary Weapon Vault.

The integration passed after restoring the five required `OBJ_VV_Weapons_*` Object Stats definitions and rebuilding the PAK.

Tutorial Chest Summoning is currently a development/test fixture and is **not** a Vaelgor's Vault dependency.

### One-Handed Weapon Vault entries

Five One-Handed Weapon Vault categories were added to `TUT_Chest_Potions` following the validated original Weapon Vault pattern. Their presence in `TreasureTable.txt`, staging, and the generated PAK is confirmed; a newly summoned Tutorial Chest has not yet been tested in-game with these new entries.

`TreasureTable.txt` remains unified until multi-file TreasureTable merge behavior is directly verified in-game.

## 15. Localization

### Status

**PASS**

All five Weapon Vaults display their correct English names and descriptions in-game:

- Common;
- Uncommon;
- Rare;
- Very Rare;
- Legendary.

### Historical issue

Common, Uncommon, Very Rare and Legendary initially displayed:

```text
Not Found
Not Found
```

The physical containers and autosort remained functional.

A read-only Codex audit confirmed that the 12 localization handles used by the four new RootTemplates did not match the corresponding `contentuid` values in:

```text
src\Localization\English\VaelgorsVault_CustomContainers.xml
```

Rare already matched correctly and was preserved as the known-good control.

### Fix

Only the 12 localization handles for:

- Common;
- Uncommon;
- Very Rare;
- Legendary;

were changed in `VV_WeaponVaults.lsx` to match the existing English XML handles.

Rare was preserved unchanged.

Static verification reported:

```text
localization_unmatched=0
```

for all five Vaults.

The rebuilt PAK and in-game test confirmed the fix.

The English localization remains in one XML/LOCA pair until multi-file LOCA behavior is directly verified in-game.

## 16. Current dependencies / test fixtures

Current clean test environment has temporarily used:

- Tutorial Chest Summoning;
- Evelyn Dagger.

They are **development fixtures**, not declared dependencies of Vaelgor's Vault.

Current mod core depends on Script Extender Lua functionality.

Do not publish Evelyn or Tutorial Chest Summoning as required dependencies unless a future design decision explicitly changes this.

## 17. Out-of-scope for current phase

Do not implement yet:

- world pickup/collection;
- aura collectors;
- corpse scanning;
- remote pickup;
- automatic world-container harvesting;
- MCM;
- end-user runtime container creation;
- dynamic custom names/descriptions;
- loot/balance/economy mechanics.

World collection may be evaluated later as an optional/separate feature.

## 18. Current priority order

1. Inspect the `Kingsknife` Stats classification before changing any classifier.
2. Test the ByType Vaults in-game: spawn/delivery, localization, storage, save/reload, and removal/rollback behavior.
3. Test interaction with the existing inventory hotkey/reorganization mod:
   - keep a weapon manually outside its Vault;
   - trigger inventory reorganize hotkey;
   - observe whether `TemplateAddedTo` causes Vaelgor autosort.
4. Record the current Weapon implementation as the first stable functional baseline.
5. Clean repository-only development artifacts.
6. Initialize Git and create the first private GitHub repository/commit.
7. Preserve the current Weapon implementation unless a concrete regression appears.
8. Choose and implement the next item family using the Weapon Vault pattern.
9. Evaluate broader compatibility, installation, update/removal and release requirements later.

## 19. Known good baseline

Current known-good functional core:

- five physical Weapon Vault containers;
- Core Rarity and ByType RootTemplate LSX files for the complete Weapon family;
- correct Object Stats for all five Vaults;
- correct English localization for all five Vaults;
- Tutorial Chest delivery for all five Vaults;
- runtime weapon detection;
- runtime rarity detection confirmed for `0` through `4`;
- Type × Rarity autosort for Daggers, Ranged, Two-Handed, and One-Handed weapons;
- Core Rarity fallback for unresolved classification or unavailable ByType Vaults;
- `Take All` behavior with autosort;
- manual withdrawal exception;
- persistent withdrawal state;
- save/reload persistence;
- accepted drop behavior;
- multi-rarity routing for Common/Uncommon/Rare/Very Rare/Legendary;
- working LSX → LSF conversion;
- working XML → LOCA conversion;
- generated PAK structurally validated;
- generated/staged Object Stats validated.

Pending only if not yet directly tested:

- `Kingsknife` Stats classification; it currently uses the safe Core Rarity fallback;
- compatibility behavior with the existing inventory reorganization hotkey.

If a future change causes a serious regression:

**Rollback to this functional baseline instead of redesigning multiple systems simultaneously.**

## 20. Repository / version-control status

The project has reached a functional baseline suitable for initial version control.

Current repository preparation goals:

- remove accidental npm artifacts:
  - `node_modules/`
  - `package.json`
  - `package-lock.json`
- exclude `.venv/`;
- exclude `Build/` and generated PAK artifacts;
- exclude user-specific PyCharm/IDE files;
- exclude Python cache/temp files;
- exclude third-party reference material from `References/` unless redistribution permission is explicitly confirmed;
- preserve all Vaelgor source, documentation and build tooling.

Recommended first repository state:

- repository name: `VaelgorsVault`;
- visibility: **private** during current development;
- default branch: `main`;
- initial baseline commit:
  `feat: establish weapon vault autosort baseline`

Local Git repository initialized with default branch `main`.

The initial baseline commit is staged but pending a configured Git author name and email. No author identity was invented.

GitHub CLI is not available in the current development environment, so private remote creation and push remain pending authenticated GitHub availability. No GitHub credential or alternative publishing mechanism was improvised.
