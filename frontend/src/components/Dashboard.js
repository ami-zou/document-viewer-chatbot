import React, { useEffect, useState } from "react";
import axios from "axios";
import { useParams, useLocation } from "react-router-dom";
import FileExplorer from "./FileExplorer";

const Dashboard = () => {
  const location = useLocation();
  const token = location.state.token;
  //   console.log("token passed is ", token);
  const [responseData, setResponseData] = useState([]);
  const [userProfile, setUserProfile] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchUserDashboard = async () => {
      try {
        const response = await axios.get(`http://localhost:8000/dashboard`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        console.log(response);
        setResponseData(response.data);
        console.log(typeof response);
        console.log(response.data);
      } catch (error) {
        console.error("Error fetching user dashboard:", error.message);
      }
      setLoading(false);
    };

    fetchUserDashboard();
  }, [token]);

  return (
    <div>
      <h1>{location.state.username}'s Dashboard</h1>

      {loading ? (
        <p>Loading...</p>
      ) : (
        <div>
          {/* <pre>{JSON.stringify(responseData, null, 2)}</pre> */}

          {/* File Explorer */}
          <FileExplorer files={responseData.files} />
        </div>
      )}
    </div>
  );
};

export default Dashboard;
