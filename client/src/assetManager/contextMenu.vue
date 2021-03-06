<template>
  <ContextMenu :visible="visible" :left="left + 'px'" :top="top + 'px'" @close="close">
    <li @click="rename">Rename</li>
    <li @click="remove">Remove</li>
  </ContextMenu>
</template>

<script lang="ts">
import Vue from "vue";

import Component from "vue-class-component";

import ContextMenu from "@/core/components/contextmenu.vue";
import ConfirmDialog from "@/core/components/modals/confirm.vue";
import Prompt from "@/core/components/modals/prompt.vue";

import { socket } from "@/assetManager/socket";
import { assetStore } from "@/assetManager/store";
import { getComponent, getRef } from "@/core/utils";

@Component({
    components: {
        ContextMenu,
    },
})
export default class AssetContextMenu extends Vue {
    visible = false;
    left = 0;
    top = 0;
    open(event: MouseEvent, inode: number) {
        if (!assetStore.selected.includes(inode)) getComponent<any>().select(event, inode);

        this.visible = true;
        this.left = event.pageX;
        this.top = event.pageY;
        this.$nextTick(() => {
            this.$children[0].$el.focus();
        });
    }
    close() {
        this.visible = false;
    }
    rename() {
        if (assetStore.selected.length !== 1) return;
        const asset = assetStore.idMap.get(assetStore.selected[0])!;

        getRef<Prompt>("prompt")
            .prompt("New name:", `Renaming ${asset.name}`)
            .then(
                (name: string) => {
                    socket.emit("Asset.Rename", {
                        asset: asset.id,
                        name,
                    });
                    asset.name = name;
                    getComponent().$forceUpdate();
                },
                () => {},
            );
        this.close();
    }
    remove() {
        if (assetStore.selected.length === 0) return;
        getRef<ConfirmDialog>("confirm")
            .open("Are you sure you wish to remove this?")
            .then(
                (result: boolean) => {
                    if (result) {
                        for (const sel of assetStore.selected) {
                            socket.emit("Asset.Remove", sel);
                            if (assetStore.files.includes(sel))
                                assetStore.files.splice(assetStore.files.indexOf(sel), 1);
                            else assetStore.folders.splice(assetStore.folders.indexOf(sel), 1);
                        }
                        assetStore.clearSelected();
                    }
                },
                () => {},
            );
        this.close();
    }
}
</script>