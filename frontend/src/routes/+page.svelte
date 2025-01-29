<script>
  import { userState } from "../store";
</script>

{#if $userState.isLoggedIn}
  <!-- 已登录时显示 -->
  <h1>Welcome to the Home Page</h1>
  <p>Hello, {$userState.username}!</p>
  <p>You can now access all features from the navigation bar.</p>
{:else}
  <!-- 未登录时显示 -->
  <div class="auth-container">
    <h1>Welcome!</h1>
    <p>Please login or register to continue.</p>
    <div class="buttons">
      <button on:click={() => (window.location.href = "/login")}>Login</button>
      <button on:click={() => (window.location.href = "/register")}>Register</button>
    </div>
  </div>
{/if}

<style>
  .auth-container {
    text-align: center;
    margin-top: 50px;
  }

  .auth-container h1 {
    font-size: 2rem;
    color: #007acc;
  }

  .auth-container p {
    margin: 20px 0;
    font-size: 1.2rem;
  }

  .buttons {
    display: flex;
    justify-content: center;
    gap: 20px;
  }

  .buttons button {
    padding: 10px 20px;
    font-size: 1rem;
    background-color: #007acc;
    color: white;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    transition: background-color 0.3s;
  }

  .buttons button:hover {
    background-color: #005fa3;
  }
</style>
