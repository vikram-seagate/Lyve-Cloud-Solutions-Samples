import { createRouter, createWebHistory } from "vue-router";
import HomeView from "../views/HomeView.vue";
import SignUp from "../views/SignUp.vue";
import Login from "../views/Login.vue";
import DashboardProfile from "../views/dashboard/Profile.vue";
import Connection from "../views/dashboard/Connection.vue";
import ConnectionDetail from "../views/dashboard/ConnectionDetail.vue";
import ConnectionCreate from "../views/dashboard/ConnectionCreate.vue";
import BucketList from "../views/dashboard/Bucket/List.vue";
import BucketEdit from "../views/dashboard/Bucket/Edit.vue";
import BucketCreate from "../views/dashboard/Bucket/Create.vue";

import MigrationList from "../views/dashboard/Migration/List.vue";
import MigrationCreate from "../views/dashboard/Migration/Create.vue";
import MigrationDetail from "../views/dashboard/Migration/Detail.vue";

const routes = [
  {
    path: "/",
    name: "home",
    component: HomeView,
  },
  {
    path: "/about",
    name: "about",
    // route level code-splitting
    // this generates a separate chunk (about.[hash].js) for this route
    // which is lazy-loaded when the route is visited.
    component: () =>
      import(/* webpackChunkName: "about" */ "../views/AboutView.vue"),
  },
  {
    path: "/sign-up",
    name: "signup",
    component: SignUp,
  },
  {
    path: "/login",
    name: "login",
    component: Login,
  },
  {
    path: "/dashboard/profile",
    name: "dashboard-profile",
    component: DashboardProfile,
  },
  {
    path: "/dashboard/connection",
    name: "dashboard-conn",
    component: Connection,
  },
  {
    path: "/dashboard/connection/:id",
    name: "dashboard-conn-detail",
    component: ConnectionDetail,
  },
  {
    path: "/dashboard/connection/create",
    name: "dashboard-conn-create",
    component: ConnectionCreate,
  },
  {
    path: "/dashboard/buckets",
    name: "db-buckets-list",
    component: BucketList,
  },
  {
    path: "/dashboard/buckets/:id",
    name: "db-buckets-detail",
    component: BucketEdit,
  },
  {
    path: "/dashboard/buckets/create",
    name: "db-buckets-create",
    component: BucketCreate,
  },
  {
    path: "/dashboard/migrations",
    name: "db-migrations-list",
    component: MigrationList,
  },
  {
    path: "/dashboard/migrations/create",
    name: "db-migrations-create",
    component: MigrationCreate,
  },
  {
    path: "/dashboard/migrations/:id",
    name: "db-migrations-detail",
    component: MigrationDetail,
  },
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
});

export default router;
