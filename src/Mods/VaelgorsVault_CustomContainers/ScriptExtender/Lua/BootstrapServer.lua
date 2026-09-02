Ext.Utils.Print("[Vaelgor's Vault] BootstrapServer loaded")


-- =========================================================
-- Weapon Vaults
-- =========================================================

local WEAPON_VAULTS = {
    [0] = {
        Name = "Common",
        RootTemplate = "92f192d9-e70f-44b0-9d6a-a00ecbe8ca17",
        RuntimeTemplate = "VV_Weapons_Common_92f192d9-e70f-44b0-9d6a-a00ecbe8ca17"
    },

    [1] = {
        Name = "Uncommon",
        RootTemplate = "0bfcd877-4dac-4829-a9f7-72fecaad9643",
        RuntimeTemplate = "VV_Weapons_Uncommon_0bfcd877-4dac-4829-a9f7-72fecaad9643"
    },

    [2] = {
        Name = "Rare",
        RootTemplate = "70fbde6f-a5bb-4305-a522-08f97ee6941b",
        RuntimeTemplate = "VV_Weapons_Rare_70fbde6f-a5bb-4305-a522-08f97ee6941b"
    },

    [3] = {
        Name = "Very Rare",
        RootTemplate = "25ea810a-1651-48ff-bf81-5e87c25276cd",
        RuntimeTemplate = "VV_Weapons_VeryRare_25ea810a-1651-48ff-bf81-5e87c25276cd"
    },

    [4] = {
        Name = "Legendary",
        RootTemplate = "36d997e4-7b9e-4117-803c-61d39c5fa72d",
        RuntimeTemplate = "VV_Weapons_Legendary_36d997e4-7b9e-4117-803c-61d39c5fa72d"
    }
}


local function MakeVault(name, rootTemplate)
    return {
        Name = name,
        RootTemplate = rootTemplate,
        RuntimeTemplate = name .. "_" .. rootTemplate
    }
end


local BY_TYPE_WEAPON_VAULTS = {
    Daggers = {
        [0] = MakeVault("VV_Daggers_Common", "e2be7ca4-5e99-43a3-9d4b-e0a55da22fa6"),
        [1] = MakeVault("VV_Daggers_Uncommon", "2b45683c-01c3-47b4-a47a-6d1729d56b7b"),
        [2] = MakeVault("VV_Daggers_Rare", "873a2cd0-9952-41b5-b0d2-0e85947bbce5"),
        [3] = MakeVault("VV_Daggers_VeryRare", "6ee8e987-ebc4-467f-b2d4-8886aa960f4c"),
        [4] = MakeVault("VV_Daggers_Legendary", "e6a8e362-3647-43dd-aa3f-b430d29e0423")
    },

    Ranged = {
        [0] = MakeVault("VV_RangedWeapons_Common", "aa474431-2cde-4959-a7c1-069dffdeb469"),
        [1] = MakeVault("VV_RangedWeapons_Uncommon", "30c376fe-c0d7-4a40-af0a-9567c010d3b9"),
        [2] = MakeVault("VV_RangedWeapons_Rare", "4a81581f-d186-443a-a190-de6e7cb004ea"),
        [3] = MakeVault("VV_RangedWeapons_VeryRare", "42e7356f-7396-490c-a0ba-c9ed9ff87ce0"),
        [4] = MakeVault("VV_RangedWeapons_Legendary", "73d1ebb3-8579-4a91-b782-a1bbfc08e4c0")
    },

    TwoHanded = {
        [0] = MakeVault("VV_TwoHandedWeapons_Common", "fd7780b2-cd2b-4271-af6b-a992c170db1f"),
        [1] = MakeVault("VV_TwoHandedWeapons_Uncommon", "18900e0d-e5b9-4d91-a74c-28d953e89283"),
        [2] = MakeVault("VV_TwoHandedWeapons_Rare", "15f0f8f5-9425-476f-aab4-50d14f3c2c66"),
        [3] = MakeVault("VV_TwoHandedWeapons_VeryRare", "a2c544d1-9e25-4300-a522-cf04943f5353"),
        [4] = MakeVault("VV_TwoHandedWeapons_Legendary", "0e86d258-6675-4dd3-81dd-0d6de751e10f")
    },

    OneHanded = {
        [0] = MakeVault("VV_OneHandedWeapons_Common", "4b7da40d-596b-42d4-be19-9e1aa13fded0"),
        [1] = MakeVault("VV_OneHandedWeapons_Uncommon", "c304459c-f469-43ea-b40f-6090be22f25d"),
        [2] = MakeVault("VV_OneHandedWeapons_Rare", "0947a3b8-5b1e-48e2-a7e2-339131b25890"),
        [3] = MakeVault("VV_OneHandedWeapons_VeryRare", "699486a3-d436-48b2-9fd5-bb469fa59761"),
        [4] = MakeVault("VV_OneHandedWeapons_Legendary", "d53ded6c-cd58-4040-b494-4df9e1c8656f")
    }
}


-- =========================================================
-- Persistent weapon state
-- =========================================================

Ext.Vars.RegisterUserVariable("VV_WeaponState", {
    Server = true,
    Client = false,
    WriteableOnServer = true,
    Persistent = true
})


-- =========================================================
-- Helpers
-- =========================================================

local function GetItemRarity(item)
    local entity = Ext.Entity.Get(item)

    if entity == nil or entity.Value == nil then
        return nil
    end

    return entity.Value.Rarity
end


local function ContainsValue(values, value)
    if type(values) ~= "table" then
        return false
    end

    for _, candidate in pairs(values) do
        if candidate == value then
            return true
        end
    end

    return false
end


local function GetWeaponType(item)
    local statId = Osi.GetStatString(item)

    if statId == nil or statId == "" then
        return nil
    end

    local stat = Ext.Stats.Get(statId)

    if stat == nil then
        return nil
    end

    local proficiencyGroup = stat["Proficiency Group"]
    local slot = stat["Slot"]
    local weaponProperties = stat["Weapon Properties"]

    if ContainsValue(proficiencyGroup, "Daggers") then
        return "Daggers"
    end

    if slot == "Ranged Main Weapon" then
        return "Ranged"
    end

    if ContainsValue(weaponProperties, "Twohanded") then
        return "TwoHanded"
    end

    if slot == "Melee Main Weapon" or slot == "Melee Offhand Weapon" then
        return "OneHanded"
    end

    return nil
end


local function SetManualWithdrawalReady(item)
    local entity = Ext.Entity.Get(item)

    if entity == nil then
        return
    end

    entity.Vars.VV_WeaponState = {
        ManualWithdrawalReady = true
    }
end


local function ConsumeManualWithdrawal(item)
    local entity = Ext.Entity.Get(item)

    if entity == nil then
        return false
    end

    local state = entity.Vars.VV_WeaponState

    if state == nil or state.ManualWithdrawalReady ~= true then
        return false
    end

    entity.Vars.VV_WeaponState = {
        ManualWithdrawalReady = false
    }

    return true
end


local function ClearManualWithdrawal(item)
    local entity = Ext.Entity.Get(item)

    if entity == nil then
        return false
    end

    local state = entity.Vars.VV_WeaponState

    if state == nil or state.ManualWithdrawalReady ~= true then
        return false
    end

    entity.Vars.VV_WeaponState = {
        ManualWithdrawalReady = false
    }

    return true
end


local function GetWeaponVaultByRuntimeTemplate(runtimeTemplate)
    for _, vault in pairs(WEAPON_VAULTS) do
        if vault.RuntimeTemplate == runtimeTemplate then
            return vault
        end
    end

    for _, vaultsByRarity in pairs(BY_TYPE_WEAPON_VAULTS) do
        for _, vault in pairs(vaultsByRarity) do
            if vault.RuntimeTemplate == runtimeTemplate then
                return vault
            end
        end
    end

    return nil
end


local function GetTargetVault(item, rarity, owner)
    local coreVault = WEAPON_VAULTS[rarity]

    if coreVault == nil then
        return nil, nil, true
    end

    local weaponType = GetWeaponType(item)

    if weaponType == nil then
        return coreVault, nil, true
    end

    local vaultsByRarity = BY_TYPE_WEAPON_VAULTS[weaponType]
    local typeVault = vaultsByRarity and vaultsByRarity[rarity]

    if typeVault == nil then
        return coreVault, weaponType, true
    end

    local vault = Osi.GetItemByTemplateInInventory(
        typeVault.RootTemplate,
        owner
    )

    if vault == nil or vault == "" then
        return coreVault, weaponType, true
    end

    return typeVault, weaponType, false
end


-- =========================================================
-- Autosort
-- =========================================================

Ext.Osiris.RegisterListener(
    "TemplateAddedTo",
    4,
    "after",
    function(objectTemplate, object, inventoryHolder, addType)

        if Osi.IsWeapon(object) ~= 1 then
            return
        end

        local directOwner = Osi.GetDirectInventoryOwner(object)

        if directOwner == nil or directOwner == "" then
            return
        end

        local directOwnerTemplate = Osi.GetTemplate(directOwner)

        -- Se a arma entrou diretamente em qualquer Weapon Vault,
        -- permitimos uma futura retirada manual.
        local currentVault =
            GetWeaponVaultByRuntimeTemplate(directOwnerTemplate)

        if currentVault ~= nil then
            SetManualWithdrawalReady(object)

            Ext.Utils.Print(
                "[Vaelgor's Vault] "
                .. currentVault.Name
                .. " weapon stored; manual withdrawal armed: "
                .. tostring(object)
            )

            return
        end

        -- O autosort só trabalha quando a arma está diretamente
        -- no inventário de um jogador.
        if Osi.IsPlayer(directOwner) ~= 1 then
            if ClearManualWithdrawal(object) then
                Ext.Utils.Print(
                    "[Vaelgor's Vault] Manual withdrawal cleared: "
                    .. tostring(object)
                )
            end

            return
        end

        local rarity = GetItemRarity(object)

        Ext.Utils.Print(
            "[Vaelgor's Vault] ADD: "
            .. tostring(object)
            .. " | rarity="
            .. tostring(rarity)
            .. " | directOwner="
            .. tostring(directOwner)
            .. " | addType="
            .. tostring(addType)
        )

        -- Respeita retirada manual de qualquer Weapon Vault.
        if ConsumeManualWithdrawal(object) then
            Ext.Utils.Print(
                "[Vaelgor's Vault] Manual withdrawal allowed: "
                .. tostring(object)
            )

            return
        end

        local targetVault, weaponType, useCoreFallback = GetTargetVault(
            object,
            rarity,
            directOwner
        )

        if targetVault == nil then
            return
        end

        Ext.Utils.Print(
            "[Vaelgor's Vault] type="
            .. tostring(weaponType or "unknown")
            .. " rarity="
            .. tostring(rarity)
            .. " target="
            .. (useCoreFallback and "core" or targetVault.RootTemplate)
        )

        local vault = Osi.GetItemByTemplateInInventory(
            targetVault.RootTemplate,
            directOwner
        )

        if vault == nil or vault == "" then
            Ext.Utils.Print(
                "[Vaelgor's Vault] "
                .. targetVault.Name
                .. " Weapon Vault not found."
            )

            return
        end

        Ext.Utils.Print(
            "[Vaelgor's Vault] Sorting "
            .. targetVault.Name
            .. " weapon into vault: "
            .. tostring(object)
        )

        Osi.ToInventory(
            object,
            vault,
            1,
            0,
            0
        )
    end
)
