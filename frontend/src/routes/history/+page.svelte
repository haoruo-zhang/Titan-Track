<script>
    import { onMount } from "svelte";
    import { userState } from "../../store";
  
    let username = $userState.username; // 当前登录的用户名
    let videoHistory = []; // 历史记录列表
    let errorMessage = "";
  
    // 获取历史记录
    async function fetchHistory() {
      try {
        const formData = new FormData();
        formData.append("username", username);

        const response = await fetch("http://localhost:8000/history", {
          method: "POST",
          body: formData,
        });

        const result = await response.json();

        if (response.ok) {
          videoHistory = result.videos;
        } else {
          errorMessage = result.message || "Failed to fetch history.";
        }
      } catch (error) {
        console.error("Error fetching history:", error);
        errorMessage = "An error occurred while fetching history.";
      }
    }
  
    onMount(() => {
      fetchHistory();
    });
  </script>
  
  <style>
    .history-container {
      max-width: 800px;
      margin: 20px auto;
      padding: 20px;
      background: #f9f9f9;
      border-radius: 10px;
      box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
  
    .video-item {
      margin-bottom: 15px;
      padding: 10px;
      border: 1px solid #ddd;
      border-radius: 5px;
      background: #fff;
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
  
    .video-item video {
      width: 100%;
      margin-top: 10px;
    }
  
    .error-message {
      color: red;
      font-weight: bold;
      text-align: center;
    }
  </style>
  
  <div class="history-container">
    <h1>Your Upload History</h1>
  
    {#if errorMessage}
      <p class="error-message">{errorMessage}</p>
    {:else if videoHistory.length === 0}
      <p>No videos found in your history.</p>
    {:else}
      {#each videoHistory as video}
        <div class="video-item">
          <p><strong>Filename:</strong> {video.filename}</p>
          <p><strong>Uploaded At:</strong> {video.timestamp}</p>
          <video controls>
            <source src={`http://localhost:8000/${video.path}`} type="video/mp4" />
            Your browser does not support the video tag.
          </video>
        </div>
      {/each}
    {/if}
  </div>
  