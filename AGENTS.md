# AGENTS.md — Vaelgor Mods

## Project identity
- Project: **Vaelgor Mods**
- Modder identity: **Vaelgor**
- Assistant/context name: **Lumi**
- Initial game target: **Baldur's Gate 3 (PC)**
- Current mod: **Vaelgor's Vault - Custom Containers**
- Development environment: **Windows + PyCharm + PowerShell**
- Build tooling may include BG3 Mod Manager, BG3 Script Extender, LSLib/Divine, MCM, Git/GitHub and extracted vanilla files.

## Core objective
Develop useful, stable, configurable and well-documented BG3 mods with emphasis on:
- QoL;
- customization;
- compatibility;
- low invasiveness;
- save safety;
- modular architecture;
- understandable implementation.

The user is learning modding. Do not only deliver code: explain **what changes, why, where, risks, rollback and next test**.

## Permanent engineering rules

### Evidence hierarchy
Use this priority when researching or validating implementation details:
1. official code/documentation;
2. BG3 Script Extender/API;
3. MCM documentation;
4. extracted vanilla files;
5. original mod author repository;
6. Nexus/Mod.io description, requirements and changelog;
7. recent issues/posts;
8. community references;
9. inference.

Classify uncertain claims when relevant:
- **Confirmed** — documented or directly verified;
- **Probable** — technically consistent but not yet directly tested;
- **Needs verification** — version/API/template/load-order/test dependent.

Never invent:
- Lua functions;
- Script Extender events/signatures;
- LSX/LSF fields;
- UUID/GUID values;
- RootTemplates;
- tags;
- Stats properties;
- runtime behavior.

If critical evidence is missing, inspect files/documentation before implementing.

### Vanilla vs mod vs Script Extender
Always separate:
- vanilla behavior;
- behavior introduced by Vaelgor's Vault;
- behavior introduced by third-party mods;
- Script Extender functionality;
- D&D 5e concepts.

When relevant, distinguish:
- RootTemplate;
- ParentTemplate;
- VisualTemplate;
- Icon;
- Stats;
- Tags;
- Scripts;
- Inventory flags;
- Container filters;
- AutoAdd;
- runtime behavior.

Reusing a visual must never imply reusing autosort, Stats, tags or scripts without verification.

### Development flow
Default workflow:
`problem → requirements → research → hypothesis → minimal implementation → test → validation → expansion → documentation → release`

During diagnosis:
- change **one variable at a time**;
- preserve the last known-good build;
- prefer direct verification over speculative redesign;
- do not refactor working code merely for theoretical cleanliness;
- advance incrementally on a validated baseline;
- if a new change causes a serious regression, rollback to the last known-good state.

When instructing edits:
- **SUBSTITUIR** = replace an existing block/file;
- **ACRESCENTAR** = add new content;
- identify the exact file/location whenever possible.

### Architecture
Prefer:
- modular responsibilities;
- low coupling;
- independent patches/addons instead of editing third-party mods;
- data-driven configuration when useful;
- runtime logic only where it adds clear value;
- specialized external systems when they already solve a separate problem better.

Do not add gameplay mechanics, cheats, balance changes, loot changes, economy changes or narrative changes when UI/QoL is sufficient.

### Save safety
Save preservation is a priority.

Before structural changes:
- create/keep a manual backup save;
- preserve the last working mod build;
- record current configuration;
- define rollback.

Never casually recommend removing a structural mod from an active campaign.

Before removing a mod that adds persistent items/templates/spells/passives/classes/containers/entities:
1. check author procedure;
2. remove items/effects when needed;
3. save in a safe state;
4. test on a copy;
5. only then remove.

“Game launches” does not mean “mod is compatible.”

### Compatibility checklist
For relevant releases, verify where applicable:
- BG3 Patch/Hotfix;
- Script Extender minimum;
- MCM;
- ImpUI;
- BG3MM;
- load order;
- dependencies;
- incompatibilities;
- multiplayer;
- controller/gamepad;
- existing saves;
- updates from previous versions;
- removal/uninstallation;
- UI/template/script conflicts.

Author instructions override generic load-order rules.

### Testing
Create a test checklist per feature/mod. Common categories:
- installation;
- creation/spawn;
- primary function;
- save/reload;
- Long Rest;
- region change;
- inventory;
- companions;
- Traveller's Chest;
- UI;
- dependencies;
- update;
- removal/rollback.

Record tests as:
`Test → Expected → Observed → Result → Evidence`

Do not fix multiple unrelated problems in one diagnostic step.

### Versioning and repository
Prefer SemVer:
- `0.1.0` = first functional implementation;
- `0.x.0` = new functionality;
- `0.x.y` = fix;
- `1.0.0` = first stable release.

Maintain where relevant:
- README;
- CHANGELOG;
- Requirements;
- Installation;
- Uninstallation;
- Compatibility;
- Known Issues;
- Credits;
- License.

Use Git early when the project structure is useful.
- Keep commits small and descriptive.
- Do not commit temporary files/build outputs unless intentionally required.
- Do not commit third-party reference assets/code without permission.
- Warn when the project is ready for repository creation, release, portfolio or public presentation.

### Licenses and third-party material
License/permission constraints are architectural requirements.

Before reusing:
- code;
- assets;
- icons;
- modified templates;
- third-party organized UUID data;
- any redistributable resource;

verify:
- license;
- permissions;
- attribution;
- redistribution requirements.

Public availability is not permission to reuse.

Prefer independent implementation when it reduces restrictions/dependencies.

## Vaelgor's Vault — design rules

### Product concept
“Custom Containers” means **Vaelgor creates polished predefined containers; users use them**.

It does **not** currently mean a runtime container creator/customizer for end users.

Current first vertical slice:
**Weapon Vaults separated by rarity with automatic sorting.**

### Weapon Vault family
Current planned rarity mapping:
- Common = runtime rarity `0`;
- Uncommon = runtime rarity `1` — not yet directly validated in-game;
- Rare = `2`;
- Very Rare = `3`;
- Legendary = `4`.

RootTemplates are organized by **item family**, with rarities inside one LSX:
- `VV_WeaponVaults.lsx`
- future examples: `VV_ArmorVaults.lsx`, `VV_BookVaults.lsx`, etc.

Do not create one LSX per container unless a concrete technical reason appears.

### Current autosort philosophy
Current autosort scope is **inventory organization**, not world collection.

Do not add automatically:
- aura pickup;
- ground scanning;
- corpse scanning;
- world-container scanning;
- automatic remote pickup.

World collection, if ever implemented, should be evaluated later as an optional/separate concern.

### Manual withdrawal behavior
A validated behavior exists:
- a weapon entering a Vaelgor Weapon Vault arms manual withdrawal state;
- removing it to player inventory consumes that state and prevents immediate re-sorting;
- reinserting it into a Vault arms the state again;
- persistent state survives save/reload.

Current accepted drop behavior:
- Vault → Inventory → Ground → pickup = treated as new acquisition and autosorted;
- Vault → Ground → pickup = withdrawal intent is preserved and the weapon remains in inventory.

Do not “fix” this unless a real UX problem appears.

### Runtime state
`VV_WeaponState` is server-side and persistent.
Do not enable client synchronization unless a client/UI feature genuinely needs it.

## Tooling / build expectations
Current project build command:
```powershell
python .\Tools\Build-VaelgorsVault.py --install
```

The build pipeline currently:
1. clears `Build\Staging`;
2. copies `src\Mods` and `src\Public`;
3. converts Localization XML → LOCA;
4. converts RootTemplate LSX → LSF;
5. removes staging RootTemplate LSX after conversion;
6. creates PAK using Divine/LSLib;
7. verifies expected package paths;
8. optionally installs the PAK into the BG3 Mods directory.

Current Divine executable used in development:
`C:\Tools\BG3\LSLib\Packed\Tools\Divine.exe`

Do not hard-code new user-specific paths unless already verified.

## Documentation split
- **AGENTS.md** = permanent rules, philosophy, workflow and architecture constraints.
- **Docs/STATE.md** = mutable technical state: UUIDs, versions, current files, bugs, decisions, test results, next steps.

Do not move temporary technical state into AGENTS.md.
