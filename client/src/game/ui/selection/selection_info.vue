<template>
  <div v-if="shape !== null">
    <div id="selection-menu">
      <div id="selection-edit-button" @click="openEditDialog">
        <i class="fas fa-edit"></i>
      </div>
      <div id="selection-name">{{ shape.name }}</div>
      <div id="selection-trackers">
        <template
          v-for="tracker in shape.trackers"
          v-if="tracker.name !== '' || tracker.value !== 0"
        >
          <div :key="'name-' + tracker.uuid">{{ tracker.name }}</div>
          <div
            class="selection-tracker-value"
            :key="'value-' + tracker.uuid"
            @click="changeValue(tracker, false)"
          >
            <template v-if="tracker.maxvalue === 0">{{ tracker.value }}</template>
            <template v-else>{{ tracker.value }} / {{ tracker.maxvalue }}</template>
          </div>
        </template>
      </div>
      <div id="selection-auras">
        <template v-for="aura in shape.auras" v-if="aura.name !== '' || aura.value !== 0">
          <div :key="'name-' + aura.uuid">{{ aura.name }}</div>
          <div
            class="selection-tracker-value"
            :key="'value-' + aura.uuid"
            @click="changeValue(aura, true)"
          >
            <template v-if="aura.dim === 0">{{ aura.value }}</template>
            <template v-else>{{ aura.value }} / {{ aura.dim }}</template>
          </div>
        </template>
      </div>
    </div>
    <edit-dialog ref="editDialog" :shape="shape"></edit-dialog>
  </div>
</template>

<script lang="ts">
import Vue from "vue";
import Component from "vue-class-component";

import Prompt from "@/core/components/modals/prompt.vue";
import EditDialog from "@/game/ui/selection/edit_dialog.vue";

import { getRef } from "@/core/utils";
import { socket } from "@/game/api/socket";
import { EventBus } from "@/game/event-bus";
import { layerManager } from "@/game/layers/manager";
import { Shape } from "@/game/shapes/shape";

@Component({
    components: {
        "edit-dialog": EditDialog,
    },
})
export default class SelectionInfo extends Vue {
    shape: Shape | null = null;

    mounted() {
        EventBus.$on("SelectionInfo.Shape.Set", (shape: Shape | null) => {
            this.shape = shape;
        });
    }

    beforeDestroy() {
        EventBus.$off();
    }

    openEditDialog() {
        (<any>this.$refs.editDialog).visible = true;
    }
    changeValue(object: Tracker | Aura, redraw: boolean) {
        if (this.shape === null) return;
        getRef<Prompt>("prompt")
            .prompt(`New  ${object.name} value:`, `Updating ${object.name}`)
            .then(
                (value: string) => {
                    if (this.shape === null) return;
                    const ogValue = object.value;
                    if (value[0] === "+" || value[0] === "-") object.value += parseInt(value, 10);
                    else object.value = parseInt(value, 10);
                    if (isNaN(object.value)) object.value = ogValue;
                    socket.emit("Shape.Update", { shape: this.shape.asDict(), redraw, temporary: false });
                    if (redraw) layerManager.invalidate();
                },
                () => {},
            );
    }
}
</script>

<style scoped>
#selection-menu {
    position: absolute;
    display: flex;
    flex-direction: column;
    top: 75px;
    right: 0;
    z-index: 10;
    opacity: 0.5;
    border-top-left-radius: 5px;
    border-bottom-left-radius: 5px;
    border: #82c8a0 solid 1px;
    border-right: none;
    padding: 10px 35px 10px 10px;
    background-color: #eee;
}

#selection-menu:hover {
    background-color: #82c8a0;
    opacity: 1;
}

#selection-edit-button {
    position: absolute;
    right: 10px;
    top: 10px;
    cursor: pointer;
}

#selection-trackers,
#selection-auras {
    display: grid;
    grid-template-columns: [name] 1fr [value] 1fr;
}

.selection-tracker-value,
.selection-aura-value {
    justify-self: center;
    padding: 2px;
}

.selection-tracker-value:hover,
.selection-aura-value:hover {
    cursor: pointer;
    background-color: rgba(20, 20, 20, 0.2);
}

#selection-name {
    font-size: 20px;
    font-weight: bold;
    margin-bottom: 10px;
}
</style>
