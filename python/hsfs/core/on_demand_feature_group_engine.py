#
#   Copyright 2020 Logical Clocks AB
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#

from hsfs import engine
from hsfs import feature_group as fg
from hsfs.core import feature_group_base_engine


class OnDemandFeatureGroupEngine(feature_group_base_engine.FeatureGroupBaseEngine):
    def save(self, feature_group):
        if len(feature_group.features) == 0:
            # If the user didn't specify the schema, parse it from the query
            on_demand_dataset = (
                engine.get_instance().register_on_demand_temporary_table(
                    feature_group, "read_ondmd"
                )
            )
            feature_group._features = engine.get_instance().parse_schema_feature_group(
                on_demand_dataset
            )

        self._feature_group_api.save(feature_group)

    def update_features(self, feature_group, updated_features):
        """Updates features safely."""
        # perform changes on copy in case the update fails, so we don't leave
        # the user object in corrupted state
        new_features = []
        for feature in feature_group.features:
            match = False
            for updated_feature in updated_features:
                if updated_feature.name.lower() == feature.name:
                    match = True
                    new_features.append(updated_feature)
                    break
            if not match:
                new_features.append(feature)

        copy_feature_group = fg.OnDemandFeatureGroup(
            None,
            None,
            None,
            None,
            id=feature_group.id,
            features=new_features,
        )
        self._feature_group_api.update_metadata(
            feature_group, copy_feature_group, "updateMetadata"
        )

    def append_features(self, feature_group, new_features):
        """Appends features to a feature group."""
        # perform changes on copy in case the update fails, so we don't leave
        # the user object in corrupted state
        copy_feature_group = fg.OnDemandFeatureGroup(
            None,
            None,
            None,
            None,
            id=feature_group.id,
            features=feature_group.features + new_features,
        )
        self._feature_group_api.update_metadata(
            feature_group, copy_feature_group, "updateMetadata"
        )

    def update_description(self, feature_group, description):
        """Updates the description of a feature group."""
        copy_feature_group = fg.FeatureGroup(
            None,
            None,
            description,
            None,
            id=feature_group.id,
            features=feature_group.features,
        )
        self._feature_group_api.update_metadata(
            feature_group, copy_feature_group, "updateMetadata"
        )
