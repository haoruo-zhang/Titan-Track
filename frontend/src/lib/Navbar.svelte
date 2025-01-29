<script>
  import { userState } from "../store";

  let user;
  $: userState.subscribe(value => {
    user = value;
  });

  function logout() {
    userState.set({ isLoggedIn: false, username: "" });
    localStorage.removeItem("userState");
    window.location.href = "/login";
  }
</script>

<nav>
  <div>
    <a href="/">Home</a>
    <a href="/upload">Upload</a>
    <a href="/history">History</a>
  </div>
  {#if user.isLoggedIn}
    <div class="user-info">
      Logged in as: {user.username} <button on:click={logout}>Logout</button>
    </div>
  {/if}
</nav>

<style>
  nav {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: #007acc;
    color: white;
    padding: 10px 20px;
  }

  nav .user-info button {
    padding: 5px 10px;
    background: #ff4d4d;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
  }

  nav .user-info button:hover {
    background: #e04343;
  }
</style>
