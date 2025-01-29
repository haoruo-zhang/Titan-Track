<script>
  import { userState } from "../../store";

  let username = $userState.username; // 当前用户
  let selectedFile; // 用户选择的视频文件
  let uploadedVideoPath = ""; // 上传后的视频路径
  let uploadTimestamp = ""; // 上传后返回的时间戳
  let segmentResults = []; // 分割后的视频路径列表

  // 上传视频函数
  async function uploadVideo() {
    if (!selectedFile || selectedFile.type.indexOf("video/") !== 0) {
      alert("Please select a valid video file!");
      return;
    }

    const formData = new FormData();
    formData.append("username", username);
    formData.append("file", selectedFile);

    try {
      const response = await fetch("http://localhost:8000/upload", {
        method: "POST",
        body: formData,
      });

      const result = await response.json();
      if (response.ok) {
        uploadedVideoPath = "http://localhost:8000/" + result.file_path; // 拼接完整的 URL
        uploadTimestamp = result.timestamp; // 保存时间戳
        alert(result.message);
      } else {
        alert(result.message || "Upload failed!");
      }
    } catch (error) {
      console.error("Error uploading video:", error);
      alert("An error occurred while uploading the video.");
    }
  }

  // 分析视频函数
  async function analyzeSquatSegments() {
    if (!uploadTimestamp || !uploadedVideoPath) {
      alert("Please upload a video first!");
      return;
    }

    const formData = new FormData();
    formData.append("username", username);
    formData.append("filename", selectedFile.name);
    formData.append("timestamp", uploadTimestamp);

    try {
      const response = await fetch("http://localhost:8000/analyze_squat_segments", {
        method: "POST",
        body: formData,
      });

      const result = await response.json();
      if (response.ok) {
        segmentResults = result.segments.map(segment => "http://localhost:8000/" + segment); // 拼接完整路径
        alert("Video analysis complete!");
      } else {
        alert(result.message || "Analysis failed!");
      }
    } catch (error) {
      console.error("Error analyzing video:", error);
      alert("An error occurred during analysis.");
    }
  }
</script>

<style>
  form {
    max-width: 600px;
    margin: 20px auto;
    padding: 20px;
    background: #f9f9f9;
    border-radius: 10px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  }

  label {
    display: block;
    margin-bottom: 10px;
    font-weight: bold;
  }

  input[type="file"],
  button {
    width: 100%;
    padding: 10px;
    margin-bottom: 20px;
    border: 1px solid #ddd;
    border-radius: 5px;
    box-sizing: border-box;
  }

  button {
    background-color: #007acc;
    color: white;
    font-weight: bold;
    cursor: pointer;
  }

  button:hover {
    background-color: #005fa3;
  }

  h2 {
    text-align: center;
  }

  .video-container {
    display: flex;
    flex-wrap: wrap;
    gap: 20px;
    justify-content: center;
    margin-top: 20px;
  }

  .video-container video {
    width: 300px;
    border: 2px solid #ddd;
    border-radius: 5px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  }
</style>

<h1>Upload and Analyze Video</h1>

<!-- 上传视频表单 -->
<form on:submit|preventDefault={uploadVideo}>
  <label>
    Select Video:
    <input type="file" on:change="{(e) => selectedFile = e.target.files[0]}" accept="video/*" />
  </label>
  <button type="submit">Upload</button>
</form>

<!-- 分析视频表单 -->
<form on:submit|preventDefault={analyzeSquatSegments}>
  <button type="submit" disabled={!uploadTimestamp}>Analyze</button>
</form>

<!-- 动态展示上传的视频 -->
{#if uploadedVideoPath}
  <h2>Your Uploaded Video</h2>
  <video controls>
    <source src={uploadedVideoPath} type="video/mp4" />
  </video>
{/if}

<!-- 动态展示分割视频 -->
{#if segmentResults.length > 0}
  <h2>Segmented Videos</h2>
  <div class="video-container">
    {#each segmentResults as segment}
      <video controls>
        <source src={segment} type="video/mp4" />
      </video>
    {/each}
  </div>
{/if}
