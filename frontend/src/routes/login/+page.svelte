<script>
  import { userState } from "../../store";
  let username = "";
  let password = "";

  async function login() {
    const response = await fetch("http://localhost:8000/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });

    const result = await response.json();
    if (response.ok) {
      alert("Login successful!");
      userState.set({ isLoggedIn: true, username: username }); // 设置状态
      window.location.href = "/"; // 跳转到首页
    } else {
      alert(`Error: ${result.detail}`);
    }
  }
</script>

<h1>Login</h1>
<form on:submit|preventDefault={login}>
  <label>
    Username: <input type="text" bind:value={username} required />
  </label>
  <label>
    Password: <input type="password" bind:value={password} required />
  </label>
  <button type="submit">Login</button>
</form>








