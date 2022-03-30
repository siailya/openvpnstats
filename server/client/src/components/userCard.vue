<template>
  <div class="shadow-md shadow-white/20 rounded-2xl p-4">
    <div class="text-center text-2xl font-bold flex justify-center items-center">
      <span>{{ name }}</span>
      <span class="ml-1.5 w-3 h-3 rounded-full bg-green-500" v-if="online"></span>
      <span class="ml-1.5 w-3 h-3 rounded-full bg-red-500" v-else></span>
    </div>
    <div class="text-center text-white/80 text-sm" v-if="online">
      Подключен с {{ new Date(connectedSince).toLocaleTimeString() }}
    </div>
    <hr class="border-white/30 my-3">
    <div class="text-center">
      <div class="text-lg">
        {{ avgSpeed }}<span class="text-blue-500 ml-1">Mb/s</span>
      </div>
      <div class="text-sm">
        Средняя скорость за последний час
      </div>
    </div>
    <div class="grid mt-4 grid-cols-2">
      <div class="text-center">
        <div class="text-lg">
          {{ received }}<span class="text-blue-500 ml-1">MB</span>
        </div>
        <div class="text-sm leading-none">
          Получено за последний час
        </div>
      </div>
      <div class="text-center">
        <div class="text-lg">
          {{ sended }}<span class="text-blue-500 ml-1">MB</span>
        </div>
        <div class="text-sm leading-none">
          Отправлено за последний час
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "user-card",
  props: ["sended", "received", "avgSpeed", "name", "connectedSince", "online"]
}
</script>

<style scoped>

</style>
