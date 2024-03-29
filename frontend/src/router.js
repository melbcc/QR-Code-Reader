import { createWebHistory, createRouter } from "vue-router"

const router = createRouter({
    history: createWebHistory(),
    routes: [
        {
            path: "/app/select",
            name: "Select",
            component: () => import("@/views/Select.vue"),
            meta: {
                nav: true,
                icon: "far fa-calendar-check",
            },
        },
        {
            path: "/app/scan",
            name: "Scan",
            component: () => import("@/views/Scan.vue"),
            meta: {
                nav: true,
                icon: "fas fa-camera",
            },
        },
        {
            path: "/app/list",
            name: "List",
            component: () => import("@/views/List.vue"),
            meta: {
                nav: true,
                icon: "fas fa-list",
            },
        },
    ],
    scrollBehavior(to, from, savedPosition) {
        // always scroll to the top when changing route
        return { top: 0 }
    },
})

export default router
