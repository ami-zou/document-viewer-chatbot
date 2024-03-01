// App.js

import React, { useState } from "react";
import axios from "axios";

const App = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [token, setToken] = useState("");
  const [userInfo, setUserInfo] = useState(null);

  const handleLogin = async () => {
    try {
      const response = await axios.post("http://localhost:8000/login", {
        username,
        password,
      });
      setToken(response.access_token);
    } catch (error) {
      console.error("Login error:", error);
    }
  };

  const handleGetUserInfo = async () => {
    try {
      const response = await axios.get("http://localhost:8000/users/me", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      setUserInfo(response.data);
    } catch (error) {
      console.error("Get User Info error:", error.response.data.detail);
    }
  };

  const handleLogout = async () => {
    try {
      await axios.post("http://localhost:8000/logout");
      setToken("");
      setUserInfo(null);
    } catch (error) {
      console.error("Logout error:", error.response.data.detail);
    }
  };

  return (
    <div>
      <h1>React Frontend</h1>
      <div>
        <label>Username:</label>
        <input
          type="text"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />
      </div>
      <div>
        <label>Password:</label>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
      </div>
      <div>
        <button onClick={handleLogin}>Login</button>
      </div>
      {token && (
        <div>
          <button onClick={handleGetUserInfo}>Get User Info</button>
          <button onClick={handleLogout}>Logout</button>
        </div>
      )}
      {userInfo && (
        <div>
          <h2>User Information:</h2>
          <pre>{JSON.stringify(userInfo, null, 2)}</pre>
        </div>
      )}
    </div>
  );
};

export default App;
