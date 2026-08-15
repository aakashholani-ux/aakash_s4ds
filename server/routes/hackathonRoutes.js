const express = require("express");
const router = express.Router();

const {
  createHackathon,
  getAllHackathons,
  getHackathonById,
  updateHackathon,
  deleteHackathon
} = require("../controllers/hackathonController");

// Create hackathon
router.post("/", createHackathon);

// Get all hackathons
router.get("/", getAllHackathons);

// Get single hackathon
router.get("/:id", getHackathonById);

// Update hackathon
router.put("/:id", updateHackathon);

// Delete hackathon
router.delete("/:id", deleteHackathon);

module.exports = router;