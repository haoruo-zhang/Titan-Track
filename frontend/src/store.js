import { writable } from "svelte/store";

// 检查是否在浏览器环境中
const isBrowser = typeof window !== "undefined";

// 从 localStorage 恢复状态
const storedState = isBrowser ? localStorage.getItem("userState") : null;
export const userState = writable(storedState ? JSON.parse(storedState) : { isLoggedIn: false, username: "" });

// 监听状态变化，仅在浏览器环境中同步到 localStorage
if (isBrowser) {
  userState.subscribe((value) => {
    localStorage.setItem("userState", JSON.stringify(value));
  });
}
