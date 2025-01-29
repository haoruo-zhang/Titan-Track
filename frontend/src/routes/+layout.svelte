<script>
  import Navbar from "../lib/Navbar.svelte";
  import { userState } from "../store";
</script>

{#if $userState.isLoggedIn}
  <Navbar />
{/if}

<slot />


  