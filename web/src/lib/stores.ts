import { writable, type Writable } from "svelte/store";

const themeStore = writable("dark");

const barVisible = writable(true);

const newChat: Writable<object | null> = writable(null);

export { barVisible, newChat, themeStore };
