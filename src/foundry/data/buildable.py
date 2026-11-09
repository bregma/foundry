"""Buildable template functions.

Copyright 2026 Stephen M. Webb  <stephen.webb@bregmasoft.ca>

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from pathlib import Path
from typing import LiteralString

import yaml

from foundry.config import Config
from foundry.data.crafting_tag import CraftingTag
from foundry.data.workstation_effect import WorkstationEffect

BO_TEMPLATE_NAME: LiteralString = 'BuildableObjectTemplate'
BO_OBJECT_TYPE_FIELD: LiteralString = 'type'
BO_PRD_MOD_FIELD: LiteralString = 'producer_recipeTimeModifier_str'
BO_PRD_TYPES_FIELD: LiteralString = 'producer_recipeType_tags'
BO_APT_MOD_FIELD: LiteralString = 'autoProducer_recipeTimeModifier_str'
BO_APT_TYPES_FIELD: LiteralString = 'autoProducer_recipeType_tag'
BO_MPT_MOD_FIELD: LiteralString = 'modularProducer_recipeTimeModifier_str'
BO_MPT_TYPES_FIELD: LiteralString = 'modularProducer_recipeType_tags'
BO_HAS_WS_EFFECTS_FIELD: LiteralString = 'hasWorkstationEffectManager'
BO_WS_EFFECTS_FIELD: LiteralString = 'workstationEffectTags'

BO_OBJECT_TYPE_PRODUCER: LiteralString = 'Producer'
BO_OBJECT_TYPE_AUTOPRODUCER: LiteralString = 'AutoProducer'
BO_OBJECT_TYPE_MODULERPRODUCER: LiteralString = 'ModularEntityProducer'

class Buildable:
    """Class wrapping info on a buildable item."""

    _crafting_tags: CraftingTag = None
    _workstation_effects: WorkstationEffect = None

    def __init__(self, item_id: str, config: Config) -> None:
        """Initialize a Buildable.

        Parameters
        ----------
        item_id: str
            Identifies the Buildable to load
        config: Config
            The application configuration

        """
        if Buildable._crafting_tags is None:
            Buildable._crafting_tags = CraftingTag(config)
        if Buildable._workstation_effects is None:
            Buildable._workstation_effects = WorkstationEffect(config)

        buildable_object_path = Path(config.template_base, BO_TEMPLATE_NAME, f'{item_id}.yaml')
        if config.verbose:
            print(f'--> .. attempting to load "{buildable_object_path}"')
        with buildable_object_path.open() as bf:
            buildable_yaml = yaml.safe_load(bf)
            buildable = buildable_yaml[BO_TEMPLATE_NAME][item_id]
            self.object_type             = buildable[BO_OBJECT_TYPE_FIELD]
            self.object_size             = buildable['size']
            self.requires_foundation     = buildable['hasToBeOnFoundation']
            self.is_modular_building     = bool(buildable["isModularBuilding"])
            self.power_subtype           = buildable['powerSubType']
            self.energy_consumption      = buildable['energyConsumptionKW_str']
            self.lvg_connection          = bool(buildable['hasEnergyGridConnection'])
            self.hvg_connection          = bool(buildable['hasPoleGridConnection'])
            self.hvg_connection_max      = int(buildable['poleGrid_maxConnections'])
            self.hvg_connection_range    = int(buildable['poleGrid_connectionRange'])
            self.hvg_transmission        = buildable['transformer_transmissionRate_kjPerS_str']
            self.battery_capacity        = buildable['battery_capacityKJ_str']
            self.storage_size            = buildable['storage_slotSize']
            self.has_data_system         = bool(buildable['hasDataSystemManager'])
            self.blast_resistant         = not bool(buildable['canBeDestroyedByDynamite'])

            self.recipe_multiplier       = ''
            self.recipe_producer_types   = ''
            if self.object_type == BO_OBJECT_TYPE_PRODUCER:
                self.recipe_multiplier     = str(buildable[BO_PRD_MOD_FIELD])
                self.recipe_producer_types = ', '.join([Buildable._crafting_tags.id_to_name(t)
                                                        for t in buildable[BO_PRD_TYPES_FIELD]])
            elif self.object_type == BO_OBJECT_TYPE_AUTOPRODUCER:
                self.recipe_multiplier     = str(buildable[BO_APT_MOD_FIELD])
                self.recipe_producer_types = Buildable._crafting_tags.id_to_name(buildable[BO_APT_TYPES_FIELD])
            elif self.object_type == BO_OBJECT_TYPE_MODULERPRODUCER:
                self.recipe_multiplier     = str(buildable[BO_MPT_MOD_FIELD])
                self.recipe_producer_types = ', '.join([Buildable._crafting_tags.id_to_name(t)
                                                        for t in buildable[BO_MPT_TYPES_FIELD]])
            self.ws_affects              = None

            if bool(buildable[BO_HAS_WS_EFFECTS_FIELD]):
                self.ws_affects = Buildable._workstation_effects.translate_effects_list(buildable[BO_WS_EFFECTS_FIELD])
