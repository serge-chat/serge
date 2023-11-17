import { writable, type Writable } from "svelte/store";

const themeStore = writable("dark");

const newChat: Writable<object | null> = writable(null);

export { newChat, themeStore };
