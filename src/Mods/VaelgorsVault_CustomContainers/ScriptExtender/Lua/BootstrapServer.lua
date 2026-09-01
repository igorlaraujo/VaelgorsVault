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


local function GetWeaponVaultByRuntimeTemplate(runtimeTemplate)
    for _, vault in pairs(WEAPON_VAULTS) do
        if vault.RuntimeTemplate == runtimeTemplate then
            return vault
        end
    end

    return nil
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

        local targetVault = WEAPON_VAULTS[rarity]

        if targetVault == nil then
            return
        end

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