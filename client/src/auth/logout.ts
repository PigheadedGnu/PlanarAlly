import Axios from "axios";
import Vue from "vue";
import Component from "vue-class-component";
import { Route } from "vue-router";

import { coreStore } from "@/core/store";

Component.registerHooks(["beforeRouteEnter"]);

@Component({})
export default class Logout extends Vue {
    beforeRouteEnter(to: Route, from: Route, next: ({}) => {}) {
        Axios.post("/api/logout").then(() => {
            coreStore.setAuthenticated(false);
            coreStore.setUsername("");
            next({ path: "/auth/login" });
        });
    }
}
