import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";

const Login = () => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [token, setToken] = useState(null);
  const [userInfo, setUserInfo] = useState(null);

  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();

    console.log(
      "Attempt to login user: ",
      username,
      " and password: ",
      password
    );

    try {
      const response = await axios.post("http://localhost:8000/login", null, {
        params: {
          username: username,
          password: password,
        },
      });

      console.log("Response data:", response.data);
      if (response.status === 200) {
        // Log in
        console.log("Login successful");
        setIsLoggedIn(true);

        // Set token
        setToken(response.data.access_token);

        // Redirect to Dashboard page
        navigate(`/dashboard`, {
          state: { token: response.data.access_token, username: username },
        });
        // navigate(`/dashboard?token=${encodeURIComponent(token)}`);
      } else {
        console.error("Login failed");
      }
    } catch (error) {
      console.error("Login error:", error);
    }
  };

  const handleGetUserProfile = async (username) => {
    try {
      const response = await axios.get(
        "http://localhost:8000/profiles/" + username,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      setUserInfo(response.data);
    } catch (error) {
      console.error("Get User Info error:", error);
    }
  };

  const handleLogout = async () => {
    try {
      await axios.post("http://localhost:8000/logout");
      setToken("");
      setUserInfo(null);
    } catch (error) {
      console.error("Logout error:", error);
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
          <button onClick={handleGetUserProfile}>Go to Profile</button>
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

export default Login;
