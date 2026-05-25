<template>
  <div class="hover-dropdown" @mouseenter="open" @mouseleave="close">
    <div class="dropdown-title">{{ title }}</div>
    <div v-if="isOpen" class="dropdown-menu">
      <div
        v-for="item in items"
        :key="item.path"
        class="dropdown-item"
        @click="goTo(item.path)"
      >
        {{ item.label }}
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'HoverDropdown',
  props: {
    title: {
      type: String,
      default: '上传'
    },
    items: {
      type: Array,
      default: () => []
    }
  },
  data() {
    return {
      isOpen: false
    }
  },
  methods: {
    open() {
      this.isOpen = true
    },
    close() {
      this.isOpen = false
    },
    goTo(path) {
      this.$router.push(path)
      this.close()
    }
  }
}
</script>

<style scoped>
.hover-dropdown {
  position: relative;
  display: inline-block;
}
.dropdown-title {
  padding: 8px 16px;
  cursor: default;
}
.dropdown-menu {
  position: absolute;
  top: 100%;
  left: 0;
  background-color: white;
  border: 1px solid #ccc;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  z-index: 1000;
  min-width: 120px;
}
.dropdown-item {
  padding: 8px 16px;
  cursor: pointer;
  white-space: nowrap;
}
.dropdown-item:hover {
  background-color: #f0f0f0;
}
</style>