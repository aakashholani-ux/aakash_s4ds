import React from "react";
import { Link, useLocation } from "react-router-dom";

const Navbar = () => {
  const location = useLocation();

  return (
    <nav className="navbar">
      <Link to="/" className="navbar-brand">
        ⚡ Hackathon Portal
      </Link>
      <div className="navbar-links">
        <Link to="/" className={location.pathname === "/" ? "active" : ""}>
          Hackathons
        </Link>
        <Link to="/organizer" className={location.pathname === "/organizer" ? "active" : ""}>
          Organizer Dashboard
        </Link>
      </div>
    </nav>
  );
};

export default Navbar;
