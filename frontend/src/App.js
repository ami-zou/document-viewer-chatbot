// // src/App.js

// import React from "react";
// import { BrowserRouter as Router, Route, Routes, Link } from "react-router-dom";
// import Login from "./components/Login";

// const Home = () => {
//   return (
//     <div>
//       <h1>Welcome to the Home Page!</h1>
//       <Link to="/login">
//         <button>Login</button>
//       </Link>
//     </div>
//   );
// };

// // const App = () => {
// //   return (
// //     <Router>
// //       <Route path="/" element={<Home />} />
// //       <Route path="/login" element={<Login />} />
// //     </Router>
// //   );
// // };

// function App() {
//   return (
//     <div className="App">
//       <Router>
//         {/* <AuthProvider> */}
//         <Routes>
//           <Route path="/login" element={<Login />} />
//           {/* <Route element={<PrivateRoute />}>
//             <Route path="/dashboard" element={<Dashboard />} />
//           </Route> */}
//           {/* Other routes */}
//         </Routes>
//         {/* </AuthProvider> */}
//       </Router>
//     </div>
//   );
// }

// export default App;

import React from "react";
import {
  BrowserRouter as Router,
  Route,
  Routes,
  Navigate,
} from "react-router-dom";
import Login from "./components/Login";
import Dashboard from "./components/Dashboard";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/dashboard" element={<Dashboard />} />
        {/* <PrivateRoute path="/dashboard" component={Dashboard} /> */}

        <Route path="/" element={<Navigate replace to="/login" />} />
        {/* <Route
        path="/login"
        element={isLoggedIn ? <Navigate to="/Dashboard" /> : <Login />}
      /> */}
      </Routes>
    </Router>
  );
}

export default App;
