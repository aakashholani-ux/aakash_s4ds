const express = require("express");
const cors = require("cors");
require("dotenv").config();

const { connectDB } = require("./config/db");
const hackathonRoutes = require("./routes/hackathonRoutes");
const submissionRoutes = require("./routes/submissionRoutes");

const app = express();

// Initialize MongoDB Connection (if MONGO_URI is set)
connectDB();

// Middleware
app.use(cors());
app.use(express.json());

// Routes
app.use("/api/hackathons", hackathonRoutes);
app.use("/api/submissions", submissionRoutes);

// Base route check
app.get("/", (req, res) => {
  res.send("Hackathon Management API (MongoDB Ready) is running...");
});

module.exports = app;
