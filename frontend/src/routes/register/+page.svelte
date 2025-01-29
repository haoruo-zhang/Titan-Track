<script>
  import { userState } from "../../store"; // 引入 userState
  let username = "";
  let password = "";

  async function register() {
    const response = await fetch("http://localhost:8000/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });

    const result = await response.json();
    if (response.ok) {
      alert("Registration successful!");
      userState.set({ isLoggedIn: true, username: username }); // 更新状态
      window.location.href = "/"; // 注册成功后跳转到首页
    } else {
      alert(`Error: ${result.detail}`);
    }
  }
</script>

<h1>Register</h1>
<form on:submit|preventDefault={register}>
  <label>
    Username: <input type="text" bind:value={username} required />
  </label>
  <label>
    Password: <input type="password" bind:value={password} required />
  </label>
  <button type="submit">Register</button>
</form>



  
