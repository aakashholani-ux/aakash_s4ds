const express = require("express");
const router = express.Router();
const {
  getAllHackathons,
  getHackathonById,
  updateHackathon,
  deleteHackathon
} = require("../controllers/hackathonController");

// Hackathon routes
router.get("/", getAllHackathons);
router.get("/:id", getHackathonById);
router.put("/:id", updateHackathon);
router.delete("/:id", deleteHackathon);

module.exports = router;
