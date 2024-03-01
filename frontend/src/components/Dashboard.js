import React, { useEffect, useState } from "react";
import axios from "axios";
import { useParams, useLocation } from "react-router-dom";
import { Document, Page, pdfjs } from "react-pdf";

pdfjs.GlobalWorkerOptions.workerSrc = `https://unpkg.com/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.js`;

const Dashboard = () => {
  const location = useLocation();
  const token = location.state.token;
  console.log("token passed is ", token);
  const { username } = useParams();
  const [responseData, setResponseData] = useState([]);
  const [files, setFiles] = useState([]);
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
        // setFiles(response.data.files);
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
      {/* {files.map((file, index) => (
        <div key={index}>
          <Document file={`data:application/pdf;base64,${file}`}>
            <Page pageNumber={1} />
          </Document>
        </div>
      ))} */}
      {/* <div>
        {responseData.map((item) => (
          <div key={item.id}>{item.name}</div>
        ))}
      </div> */}

      {loading ? (
        <p>Loading...</p>
      ) : (
        <div>
          {/* Render data here */}
          <pre>{JSON.stringify(responseData, null, 2)}</pre>

          <p>{responseData.username}</p>
          <p>{responseData.user}</p>
        </div>
      )}
    </div>
  );
};

export default Dashboard;
