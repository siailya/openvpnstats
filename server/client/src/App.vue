<template>
  <div class="container mx-auto px-4">
    <h1 class="text-4xl text-center font-bold mt-8 mb-8"><span class="text-blue-500">OpenVPN</span> Stats</h1>

    <div v-if="data" class="main-stats shadow-md shadow-white/20 rounded-2xl p-4 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4">
      <div class="text-center">
        <div class="text-4xl font-bold">
          {{data.online}}
        </div>
        <div class="font-thin">
          пользователя онлайн
        </div>
      </div>
      <div class="text-center mx-2">
        <div class="text-4xl font-bold">
          {{ data.received.toFixed(1) }}<span class="text-blue-500 ml-1 text-2xl">MB</span>
        </div>
        <div class="font-thin">
          загружено за последний час
        </div>
      </div>
      <div class="text-center mx-2">
        <div class="text-4xl font-bold">
          {{ data.send.toFixed(1) }}<span class="text-blue-500 ml-1 text-2xl">MB</span>
        </div>
        <div class="font-thin">
          отправлено за последний час
        </div>
      </div>
      <div class="text-center mx-2">
        <div class="text-4xl font-bold">
          {{ ((data.send + data.received) / 60 / 60 * 8).toFixed(2) }}<span class="text-blue-500 ml-1 text-2xl">Mb/s</span>
        </div>
        <div class="font-thin">
          средняя скорость за последний час
        </div>
      </div>
    </div>

    <div v-if="users" class="users mt-10 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <user-card
          v-for="u in users"
          :name="u.user_name"
          :avg-speed="((u.received + u.send) / 60 / 60 * 8).toFixed(2)"
          :connected-since="u.connected_since"
          :online="u.connected"
          :received="u.received.toFixed(1)"
          :sended="u.send.toFixed(1)"
      />
    </div>
  </div>
</template>

<script>
import UserCard from "./components/userCard.vue";
import axios from "axios"

export default {
  name: "App",
  components: {UserCard},
  data() {
    return {
      users: [],
      data: null
    }
  },
  methods: {
    loadUsers() {
      axios.get("/api/get_users_info").then(r => {
        this.users = r.data
      })
    },
    loadInfo() {
      axios.get("/api/get_stat").then(r => {
        this.data = r.data
        console.log(r.data)
      })
    }
  },
  mounted() {
    this.loadUsers()
    this.loadInfo()
    setInterval(() => {
      this.loadUsers()
    }, 30000)
  }
}
</script>

<style>
</style>
